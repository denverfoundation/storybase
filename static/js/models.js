/* Models shared across multiple storybase apps */
;(function(_, Backbone, storybase) {
  if (_.isUndefined(storybase.collections)) {
    storybase.collections = {};
  }
  var Collections = storybase.collections;

  if (_.isUndefined(storybase.models)) {
    storybase.models = {};
  }
  var Models = storybase.models;

  var Forms = storybase.forms;
  var makeRequired;
  if (Forms) {
    makeRequired = Forms.makeRequired;
  }

  /**
   * Mixin that expects the model attributes to be within an objects attribute
   * 
   * This is the way Tastypie structures its response the objects.
   */
  var TastypieCollectionMixin = Collections.TastypieMixin = {
    parse: function(response) {
      return response.objects;
    }
  };

  var TastypieModelMixin = Models.TastypieMixin = {
    url: function() {
      // Ensure data always ends in a '/', for Tastypie
      var url = Backbone.Model.prototype.url.call(this); 
      url = url + (url.charAt(url.length - 1) == '/' ? '' : '/'); 
      return url;
    }
  };

  /**
   * Collection that has an additional save method.
   *
   * This method uses a PUT request to replace entire server-side collection
   * with the models in the Backbone collection.
   */
  var SaveableCollection = Collections.SaveableCollection = Backbone.Collection.extend({
    save: function(options) {
      // TODO: Test this 
      options = options ? _.clone(options) : {};
      var collection = this;
      var success = options.success;
      options.success = function(collection, resp, options) {
        collection.reset(collection.parse(resp, options), options);
        if (success) success(collection, resp);
      };
      return (this.sync || Backbone.sync).call(this, 'update', this, options);
    }
  });

  /**
   * Model that can sync a file attribute to the server as multipart form data.
   */
  var FileUploadModel = Models.FileUploadModel = Backbone.Model.extend({
    // List if model attributes that can take uploaded files
    fileAttributes: [],

    /**
     * Return a FormData object corresponding to the model's
     * attributes
     */
    toFormData: function(options) {
      var attrs = options.attrs || this.attributes;
      var formData = new FormData();
      _.each(attrs, function(value, key) {
        // Only add non-null values as it seems like Firefox
        // encodes null values as strings with a value of 'null',
        // confusing the server-side code
        if (!_.isNull(value)) {
          formData.append(key, value); 
        }
      }, this);
      return formData;
    },

    /**
     * Custom implementation of Backbone.Model.sync that sends
     * file attributes to the server as multipart form data
     * in a hidden IFRAME.
     *
     * This is for browsers that don't support the FileReader
     * API.
     *
     * It requires the jQuery Iframe Transport to be available. 
     * See http://cmlenz.github.com/jquery-iframe-transport/ 
     */
    syncWithUploadIframe: function(method, model, options) {
      var data; // Attribute data, passed to jQuery.sync

      _.extend(options, {
        iframe: true, // Tell jQuery to use the IFRAME transport
        files: options.form.find(':file'), 
        processData: false,
        dataType: 'json',
        // We can't set the accepts header of the IFRAMEd post,
        // so explicitly ask for the response as JSON.
        url: _.result(model, 'url') + '?format=json&iframe=iframe'
      });

      if (!options.data) {
        data = options.attrs || model.toJSON(options);
        // Remove file attributes from the data
        options.data = _.omit(data, model.fileAttributes);
      }

      return Backbone.sync(method, model, options);
    },

    /**
     * Custom implementation of Backbone.Model.sync that sends
     * file attributes to the server as multipart form data.
     *
     * Additional options:
     *
     * @param {Object} [form] jQuery object for the HTML form element. This is
     *     needed if we have to POST using a hidden IFRAME in older browsers.
     * @param {function} [progressHandler] Handler function for the ``progress``
     *     event of the underlying ``XMLHttpRequest`` object.
     */
    syncWithUpload: function(method, model, options) {
      if (window.FormData && window.FileReader && !options.iframe) {
        if (!options.xhr) {
          // Wire up the upload progress handler if one has been specified
          options.xhr = function() {
            var newXhr = $.ajaxSettings.xhr();
            if (newXhr.upload && options.progressHandler) {
              newXhr.upload.addEventListener('progress', options.progressHandler, false);
            }
            return newXhr;
          };
        }
        if (!options.data) {
          // Convert model attributes to a FormData object
          options.data = model.toFormData(options);
        }

        // Set some defaults for jQuery.ajax to make sure that
        // our multipart form data will get sent correctly.
        // See http://stackoverflow.com/a/5976031
        _.extend(options, {
          cache: false,
          contentType: false,
          processData: false
        });

        return Backbone.sync(method, model, options);
      }
      else {
        // Browser (i.e. IE < 10) doesn't support the FormData interface for
        // XMLHttpRequest. Or IFRAME uploads have been explictely requested.
        // We'll have to upload using a hidden IFRAME
        this.syncWithUploadIframe(method, model, options);
      }
    },

    /**
     * Custom implementation of Backbone.Model.sync that delegates to
     * syncWithFileUpload when a file to be uploaded is present.
     *
     * Additional parameters:
     *
     * @param {Boolean} [upload] Should we attempt to upload files on sync
     * @param {Object} [form] jQuery object for the HTML form element. This is
     *     needed if we have to POST using a hidden IFRAME in older browsers.
     * @param {function} [progressHandler] Handler function for the ``progress``
     *     event of the underlying ``XMLHttpRequest`` object.
     */
    sync: function(method, model, options) {
      if (options.upload) {
        return this.syncWithUpload(method, model, options);
      }
      else {
        return Backbone.sync.apply(this, arguments);
      }
    }
  });


  var DataSet = Models.DataSet = FileUploadModel.extend({
    idAttribute: "dataset_id",

    /**
     * Return the server URL for a model instance.
     *
     * This version always uses the collection's URL if the instance is new,
     * otherwise it uses the value returned by the API.  This is needed
     * because sometimes a collection will have a URL set to fetch a
     * particular story's data sets.  By default, Backbone uses the 
     * collection's URL to build an individual model's URL.  We don't want
     * to do this.
     */
    url: function() {
      var url = Backbone.Model.prototype.url.call(this);
      if (!this.isNew() && this.has('resource_uri')) {
        url = this.get('resource_uri');
      }
      // Make sure the URL ends in a '/'
      url = url + (url.charAt(url.length - 1) == '/' ? '' : '/');
      return url; 
    },

    /**
     * Schema for backbone-forms
     */
    schema: function() {
      if (!_.isUndefined(Forms)) {
        var schema = {
          title: makeRequired({
            type: 'Text'
          }),
          source: {
            type: 'Text'
          },
          url: {
            type: 'Text',
            validators: ['url']
          },
          file: {
            type: Forms.File
          }
        };

        if (!this.isNew()) {
          // For a saved model, only show the fields that have a value set.
          _.each(['file', 'url'], function(field) {
            var value = this.get(field);
            if (!value) {
              delete schema[field];
            }
          }, this);

          // Mark a standalone URL field as required.  Don't mark the file URL as
          // required because the user doesn't have to specify a new
          // file
          if (schema.url) {
            makeRequired(schema.url);
          }
        }

        return schema;
      }
    },

    /**
     * Validate the model attributes
     *
     * Make sure only one of the content variables is set to a truthy
     * value.
     */
    validate: function(attrs) {
      var contentAttrNames = ['file', 'url'];
      var found = [];
      var msg = gettext("You must specify either the file or url field, but not both.");
      _.each(contentAttrNames, function(attrName) {
        if (_.has(attrs, attrName) && attrs[attrName]) {
          found.push(attrName);
        }
      });

      // We allow existing datasets with a file attribute to have a
      // missing file and url attributes, which is the case when updating
      // an existing dataset. Otherwise, one and only one of the fields
      // is required
      if (found.length !== 1 && (this.isNew() || !this.get('file'))) {
        return {
          file: msg,
          url: msg
        };
      }
    }
  });


  Collections.DataSets = Backbone.Collection.extend( 
    _.extend({}, TastypieCollectionMixin, {
      model: DataSet,

      initialize: function() {
        this._story = null;
        this._asset = null;
      },

      url: function() {
        var url = storybase.API_ROOT + 'datasets/';
        if (this._asset !== null) {
          url = url + 'assets/' + this._asset.id + '/';
        }
        else if (this._story !== null) {
          url = url + 'stories/' + this._story.id + '/';
        }
        return url; 
      },

      /**
       * Specify that this collection represent's a particular asset's
       * dataset.
       */
      setAsset: function(asset) {
        this._asset = asset;
      },

      /**
       * Specify that this collection represent's a particular
       * story's data sets
       */
      setStory: function(story) {
        this._story = story;
      },

      // TODO: Test this method, particularly checking which events are fired on
      // the removed model
      /**
       * Remove a single model from a collection at the server
       *
       * This method is for endpoints that support support removing an
       * item from a collection with a DELETE request to an endpoint like
       * /<collection-url>/<model-id>/.
       */
      removeSync: function(models, options) {
        models = _.isArray(models) ? models.slice() : [models];
        var i, l, index, model, url;
        for (i = 0, l = models.length; i < l; i++) {
          model = models[i]; 
          url = _.result(this, 'url') + model.id + '/';
          this.sync('delete', model, {
            url: url
          });
        }
        return this;
      },

      /**
       * Remove a model (or an array of models) from the collection.
       *
       * Unlike the default ``Collection.remove`` this takes an additional
       * ``sync`` option that, if truthy, will cause the models to be 
       * removed on the server.
       */
      remove: function(models, options) {
        var model = this;
        if (!_.isUndefined(options.sync)) {
          if(_.result(options, 'sync')) {
            this.once('remove', function() {
              model.removeSync(models, options);
            }, this);
          }
        }
        Backbone.Collection.prototype.remove.apply(this, arguments);
      }
    })
  );

  var Location = Models.Location = Backbone.Model.extend({
    idAttribute: 'location_id',

    urlRoot: function() {
      return storybase.API_ROOT + 'locations';
    },

    /**
     * Get the URL for the model.  
     *
     * Unlike the default version, for new models this uses the collection url
     * first, instead of the urlRoot value.
     */
    url: function() {
      var base = _.result(this, 'urlRoot') || _.result(this.collection, 'url') || urlError();
      if (this.isNew()) {
        base = _.result(this.collection, 'url') || _.result(this, 'urlRoot') || urlError();
        return base;
      }
      else {
        base = base + (base.charAt(base.length - 1) == '/' ? '' : '/') + encodeURIComponent(this.id);
      }
      return base + (base.charAt(base.length - 1) == '/' ? '' : '/');
    }
  });

  Collections.Locations = Backbone.Collection.extend(
    _.extend({}, TastypieCollectionMixin, {
      model: Location,

      initialize: function(models, options) {
        this._story = _.isUndefined(options.story) ? null : options.story;
      },

      url: function() {
        var url = storybase.API_ROOT + 'locations/';
        if (this._story) {
          url = url + 'stories/' + this._story.id + '/';
        }
        return url;
      },

      setStory: function(story) {
        this._story = story;
      }
    })
  );

  var Story = Models.Story = Backbone.Model.extend(
    _.extend({}, TastypieModelMixin, {
      idAttribute: "story_id",

      urlRoot: function() {
        return storybase.API_ROOT + 'stories';
      },

      defaults: {
        'title': '',
        'byline': '',
        'summary': '',
        'connected': false,
        'connected_prompt': ''
      },

      initialize: function(options) {
        this.sections = new Sections();
        this.unusedAssets = new Assets();
        this.assets = new Assets();
        this.setCollectionUrls();
        this.on("change", this.setCollectionUrls, this);
        this.sections.on("add", this.resetSectionWeights, this);
      },

      /**
       * Set the url property of collections.
       *
       * This is needed because the URL of the collections are often based
       * on the model id.
       */
      setCollectionUrls: function() {
        if (!this.isNew()) {
          this.sections.url = this.url() + 'sections/';
          this.unusedAssets.url = storybase.API_ROOT + 'assets/stories/' + this.id + '/sections/none/'; 
          this.assets.url = storybase.API_ROOT + 'assets/stories/' + this.id + '/';
        }
      },

      /**
       * Set the featured assets collection.
       */
      setFeaturedAssets: function(collection) {
        this.featuredAssets = collection;
        this.featuredAssets.setStory(this);
        this.trigger('set:featuredassets', this.featuredAssets);
      },

      /**
       * Set the related stories collection.
       */
      setRelatedStories: function(relatedStories) {
        this.relatedStories = relatedStories;
        this.relatedStories.setStory(this);
      },

      /**
       * Re-set the section weights based on their order in the collection 
       */
      resetSectionWeights: function() {
        this.sections.each(function(section, index) {
          section.set('weight', index);
        });
      },

      /**
       * Set the featured asset.
       *
       * This method provides an interface for the actual set operation
       * since it's a little unintuitive.
       */
      setFeaturedAsset: function(asset, options) {
        // The data model supports having multiple featured assets, but
        // our current use case only needs to keep one.
        options = options ? _.clone(options) : {};
        var model = this;
        var success = options.success;
        options.success = function(collection, resp, options) {
          if (success) success(collection, resp, options);
        };
        this.featuredAssets.reset(asset);
        model.trigger("set:featuredasset", asset);
        this.featuredAssets.save(options);
      },

      getFeaturedAsset: function(index) {
        index = _.isUndefined(index) ? 0 : index; 
        if (this.featuredAssets) {
          return this.featuredAssets.at(index);
        }
        else {
          return undefined;
        }
      },

      saveFeaturedAssets: function() {
        if (this.featuredAssets) {
          this.featuredAssets.save();
        }
      },

      saveRelatedStories: function() {
        if (this.relatedStories) {
          this.relatedStories.save();
        }
      },


      /**
       * Save all the sections of the story
       */
      saveSections: function(options) {
        this.sections.each(function(section) {
          section.save();
        });
      },


      /**
       * Copy selected properties from another story.
       *
       * @param {Object} story  Story model instance to use as the template
       *   for this model
       * @param {Object} sectionAttrs Attributes to set on each section
       *   copied from the template story.  These override any attribute copied
       *   from the template.
       */
      fromTemplate: function(story, sectionAttrs) {
        this.set('structure_type', story.get('structure_type'));
        this.set('summary', story.get('summary'));
        this.set('call_to_action', story.get('call_to_action'));
        this.set('template_story', story.get('story_id'));
                      
        story.sections.each(function(section) {
          var sectionCopy = new Section();
          sectionCopy.set("title_placeholder", section.get("title"));
          sectionCopy.set("title", "");
          sectionCopy.set("layout", section.get("layout"));
          sectionCopy.set("root", section.get("root"));
          sectionCopy.set("weight", section.get("weight"));
          sectionCopy.set("layout_template", section.get("layout_template"));
          sectionCopy.set("template_section", section.get("section_id"));
          sectionCopy.set("help", section.get("help"));
          if (!_.isUndefined(sectionAttrs)) {
            sectionCopy.set(sectionAttrs);
          }
          this.sections.push(sectionCopy);
        }, this);
      }
    })
  );


  Collections.Stories = Backbone.Collection.extend({
      model: Story,

      url: function() {
        return storybase.API_ROOT + 'stories';
      }
  });

  var Section = Models.Section = Backbone.Model.extend(
    _.extend({}, TastypieModelMixin, {
      idAttribute: "section_id",

      initialize: function() {
        this.assets = new SectionAssets();
        this.setCollectionUrls();
        this.on("change", this.setCollectionUrls, this);
      },

      populateChildren: function() {
        var $this = this;
        this.children = this.get('children').map(function(childId) {
          return $this.collection.get(childId).populateChildren();
        });
        return this;
      },

      /**
       * Set the url property of collections.
       *
       * This is needed because the URL of the collections are often based
       * on the model id.
       */
      setCollectionUrls: function() {
        if (!this.isNew()) {
          this.assets.url = this.url() + 'assets/';
        }
      },

      title: function() {
        return this.get("title");
      },

      urlRoot: function() {
        return storybase.API_ROOT + 'sections';
      },

      /**
       * Return the server URL for a model instance.
       *
       * This version always tries to use the model instance's collection
       * URL first.
       */
      url: function() {
        var base = _.result(this.collection, 'url') || _.result(this, 'urlRoot') || urlError();
        if (this.isNew()) {
          return base;
        }
        else {
          base = base + (base.charAt(base.length - 1) == '/' ? '' : '/') + encodeURIComponent(this.id);
        }
        return base + (base.charAt(base.length - 1) == '/' ? '' : '/');
      }
    })
  );

  var Sections = Collections.Sections = Backbone.Collection.extend(
    _.extend({}, TastypieCollectionMixin, {
      model: Section,

      url: storybase.API_ROOT + 'sections/',

      initialize: function() {
        _.bindAll(this, '_assetsFetchedSuccess', '_assetsFetchedError');
      },

      sortByIdList: function(idList) {
        var that = this;
        _.each(idList, function(id, index) {
          var section = that.get(id);
          section.set('weight', index);
        });
        this.models = this.sortBy(function(section) {
          var weight = section.get('weight');
          return weight;
        });
      },

      /**
       * Callback for when an individual section's asset is fetched.
       */
      _assetsFetchedSuccess: function(section, assets, response) {
        var callback = this._fetchAssetsSuccess ? this._fetchAssetsSuccess : null;
        this._assetsFetched.push(section.id);  
        if (this._assetsFetched.length == this.length) {
          // All the sections have been fetched!
          this._fetchAssetsCleanup();
          if (callback) {
            callback(this);
          }
        }
      },

      /**
       * Callback for when an individual section's assets failed to be 
       * fetched
       */
      _assetsFetchedError: function(section, assets, response) {
        var callback = this._fetchAssetsError ? this._fetchAssetsError : null;
        this._fetchAssetsCleanup();
        if (callback) {
          callback(this);
        }
      },

      _fetchAssetsCleanup: function() {
        this._assetsFetched = [];
        this._fetchAssetsSuccess = null; 
        this._fetchAssetsError = null; 
      },

      /**
       * Fetch the assets for each section in the collection.
       */
      fetchAssets: function(options) {
        options = options ? options : {};
        this._assetsFetched = [];
        if (options.success) {
          this._fetchAssetsSuccess = options.success;
        }
        if (options.error) {
          this._fetchAssetsError = options.error;
        }
        this.each(function(section) {
          var coll = this;
          var success = function(assets, response) {
            coll._assetsFetchedSuccess(section, assets, response);
          };
          var error = function(assets, response) {
            coll._assetsFetchedError(section, assets, response);
          };
          section.assets.fetch({
            success: success,
            error: error 
          });
        }, this);
      }
    })
  );

  var StoryRelation = Models.StoryRelation = Backbone.Model.extend({
    idAttribute: "relation_id"
  });

  Collections.StoryRelations = SaveableCollection.extend(
    _.extend({}, TastypieCollectionMixin, {
      model: StoryRelation,

      initialize: function(models, options) {
        if (!_.isUndefined(options)) {
          this.setStory(options.story);
        }
      },

      fillTargets: function() {
        this.each(function(rel) {
          if (rel.isNew()) {
            // Unsaved story relation
            if (_.isUndefined(rel.get('target'))) {
              rel.set('target', this._story.id);
            }
          }
        }, this);
      },

      save: function(options) {
        this.fillTargets();
        return SaveableCollection.prototype.save.call(this, options);
      },

      setStory: function(story) {
        this._story = story;
      },

      url: function() {
        return _.result(this._story, 'url') + 'related/';
      }
    })
  );

  var Asset = Models.Asset = FileUploadModel.extend(
    _.extend({}, TastypieModelMixin, {
      fileAttributes: ['image'],

      showFormField: {
        url: {
          'image': true,
          'audio': true,
          'video': true,
          'map': true,
          'table': true,
          'chart': true
        },

        image: {
          'image': true,
          'map': true,
          'chart': true
        },

        body: {
          'text': true,
          'quotation': true,
          'map': true,
          'table': true,
          'chart': true
        },

        caption: {
          'image': true,
          'audio': true,
          'video': true,
          'map': true,
          'table': true,
          'chart': true
        },

        attribution: {
          'quotation': true,
          'table': true,
          'chart': true
        },


        source_url: {
          'quotation': true,
          'table': true
        },

        title: {
          'table': true
        }
      },

      formFieldVisible: function(name, type) {
        return _.has(this.showFormField[name], type);
      },

      /**
       * Build the schema for backbone-forms
       *
       * This is done with a function instead of declaring an object because
       * the fields differ depending on the type of asset.
       */
      schema: function() {
        if (!_.isUndefined(Forms)) {
          var schema = {
            title: {title: gettext("Title"), type: 'Text'},
            url: {title: gettext("URL"), type: 'Text', validators: ['url']},
            image: {title: gettext("Image file"), type: Forms.File},
            body: {title: gettext("Body"), type: 'TextArea'},
            //caption: {title: gettext("Caption"), type: 'TextArea'},
            attribution: {title: gettext("Attribution"), type: 'TextArea'},
            source_url: {title: gettext("Source URL"), type: 'Text', validators: ['url']}
          };
          var type = this.get('type');
          // Remove fields that aren't relevant for a particular type
          _.each(schema, function(field, name, schema) {
            if (!this.formFieldVisible(name, type)) {
              delete schema[name];
            }
          }, this);
          if (!this.isNew()) {
            // For a saved model, only show the fields that have a value set.
            _.each(['image', 'url', 'body'], function(field) {
              var value = this.get(field);
              if (!value) {
                delete schema[field];
              }
            }, this);
          }

          return schema;
        }
      },

      idAttribute: "asset_id",

      urlRoot: function() {
        return storybase.API_ROOT + 'assets/';
      },

      /**
       * Validate the model attributes
       *
       * Make sure that only one of the content attributes is set to a truthy
       * value.
       */
      validate: function(attrs, options) {
        var contentAttrNames = ['body', 'image', 'url'];
        var found = [];
        _.each(contentAttrNames, function(attrName) {
          if (_.has(attrs, attrName) && attrs[attrName]) {
            found.push(attrName);
          }
        }, this);
        if (found.length > 1) {
          return "You must specify only one of the following values " + found.join(', ');
        }
      },

      /**
       * Can this asset type accept related data?
       */
      acceptsData: function() {
        var type = this.get('type');
        if (type === 'map' || type === 'chart' || type === 'table') {
          return true;
        }
        else {
          return false;
        }
      },

      /**
       * Set the asset's datasets collection.
       */
      setDataSets: function(collection) {
        this.datasets = collection;
        this.datasets.setAsset(this);
        this.trigger('set:datasets', this.datasets);
      }
    })
  );

  var Assets = Collections.Assets = Backbone.Collection.extend(
    _.extend({}, TastypieCollectionMixin, {
      model: Asset
    })
  );

  var SectionAssets = Collections.SectionAssets = Assets.extend({
    parse: function(response) {
      var models = [];
      _.each(response.objects, function(sectionAsset) {
        var asset = sectionAsset.asset;
        asset.container = sectionAsset.container;
        models.push(asset);
      });
      return models;
    }
  });

  Collections.FeaturedAssets = SaveableCollection.extend(
    _.extend({}, TastypieCollectionMixin, {
      model: Asset,

      initialize: function(models, options) {
        if (!_.isUndefined(options)) {
          this.setStory(options.story);
        }
      },

      save: function(options) {
        return SaveableCollection.prototype.save.call(this, options);
      },

      setStory: function(story) {
        this._story = story;
      },

      url: function() {
        return storybase.API_ROOT + 'assets/stories/' + this._story.id + '/featured/';
      }
    })
  );

  var Tag = Models.Tag = Backbone.Model.extend({
    idAttribute: "tag_id",

    /**
     * Check whether the model has been saved to the server.
     *
     * This version checks for a resource_uri attribute instead of
     * Backbone's default behavior, which is to check for a non-null id.
     * This is needed because of the API semantics which associate a new
     * tag with a story by POSTing to /API_ROOT/tags/stories/STORY_ID/
     * with a payload that includes a tag_id property. It makes sense to
     * do this with Backbone.Collection.create, but setting tag_id (this
     * model's idAttribute) causes the default isNew implementation to
     * think the model already exists and do a PUT request to the 
     * wrong url.
     */
    isNew: function() {
      return _.isUndefined(this.get('resource_uri'));
    }
  });

  Collections.Tags = Backbone.Collection.extend(
    _.extend({}, TastypieCollectionMixin, {
      model: Tag,

      initialize: function(models, options) {
        this._story = _.isUndefined(options.story) ? null : options.story;
      },

      url: function() {
        var url = storybase.API_ROOT + 'tags/';
        if (this._story) {
          url = url + 'stories/' + this._story.id + '/';
        }
        return url;
      },

      setStory: function(story) {
        this._story = story;
      }
    })
  );
})(_, Backbone, storybase);
