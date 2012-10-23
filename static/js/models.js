/* Models shared across multiple storybase apps */
Namespace('storybase.globals');
Namespace('storybase.models');
Namespace('storybase.collections');

/**
 * Mixin that expects the model attributes to be within an objects attribute
 * 
 * This is the way Tastypie structures its response the objects.
 */
storybase.collections.TastypieMixin = {
  parse: function(response) {
    return response.objects;
  }
}

storybase.models.TastypieMixin = {
  url: function() {
    // Ensure data always ends in a '/', for Tastypie
    var url = Backbone.Model.prototype.url.call(this); 
    url = url + (url.charAt(url.length - 1) == '/' ? '' : '/'); 
    return url;
  }
}

/**
 * Collection that has an additional save method.
 *
 * This method uses a PUT request to replace entire server-side collection
 * with the models in the Backbone collection.
 */
storybase.collections.SaveableCollection = Backbone.Collection.extend({
  save: function(options) {
    // TODO: Test this 
    // BOOKMARK
    options = options ? _.clone(options) : {};
    var collection = this;
    var success = options.success;
    options.success = function(resp, status, xhr) {
      collection.reset(collection.parse(resp, xhr), options);
      if (success) success(collection, resp);
    };
    options.error = Backbone.wrapError(options.error, collection, options);
    return (this.sync || Backbone.sync).call(this, 'update', this, options);
  }
});

storybase.models.DataSet = Backbone.Model.extend({
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
      if (!_.isUndefined(storybase.forms)) {
        var schema = {
          title: {type: 'Text', validators: ['required']},
          source: {type: 'Text', validators: []},
          url: {type: 'Text', validators: ['url']},
          file: {type: storybase.forms.File}
        };
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
      _.each(contentAttrNames, function(attrName) {
        if (_.has(attrs, attrName) && attrs[attrName]) {
          found.push(attrName);
        }
      });
      if (found.length > 1) {
        // TODO: Translate this
        return "You must specify only one of the following values " + found.join(', ');
      }
    }
});


storybase.collections.DataSets = Backbone.Collection.extend( 
  _.extend({}, storybase.collections.TastypieMixin, {
    model: storybase.models.DataSet,

    initialize: function() {
      this._story = null;
    },

    url: function() {
      var url = storybase.globals.API_ROOT + 'datasets/';
      if (this._story !== null) {
        url = url + 'stories/' + this._story.id + '/';
      }
      return url; 
    },

    /**
     * Specify that this collection represent's a particular
     * story's data sets
     */
    setStory: function(story) {
      this._story = story;
    }
  })
);

storybase.models.Location = Backbone.Model.extend({
  idAttribute: 'location_id',

  urlRoot: function() {
    return storybase.globals.API_ROOT + 'locations';
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

storybase.collections.Locations = Backbone.Collection.extend(
  _.extend({}, storybase.collections.TastypieMixin, {
    model: storybase.models.Location,

    initialize: function(models, options) {
      this._story = _.isUndefined(options.story) ? null : options.story;
    },

    url: function() {
      var url = storybase.globals.API_ROOT + 'locations/';
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

storybase.models.Story = Backbone.Model.extend(
  _.extend({}, storybase.models.TastypieMixin, {
    idAttribute: "story_id",

    urlRoot: function() {
      return storybase.globals.API_ROOT + 'stories';
    },

    defaults: {
      'title': '',
      'byline': '',
      'summary': '',
      'connected': false,
      'connected_prompt': ''
    },

    initialize: function(options) {
      this.sections = new storybase.collections.Sections;
      this.unusedAssets = new storybase.collections.Assets;
      this.assets = new storybase.collections.Assets;
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
        this.unusedAssets.url = storybase.globals.API_ROOT + 'assets/stories/' + this.id + '/sections/none/'; 
        this.assets.url = storybase.globals.API_ROOT + 'assets/stories/' + this.id + '/';
      }
    },

    /**
     * Set the featured assets collection.
     */
    setFeaturedAssets: function(collection) {
      this.featuredAssets = collection;
      this.featuredAssets.setStory(this);
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
    setFeaturedAsset: function(asset) {
      // The data model supports having multiple featured assets, but
      // our current use case only needs to keep one.
      this.featuredAssets.reset(asset);
      this.featuredAssets.save();
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
        var sectionCopy = new storybase.models.Section();
        sectionCopy.set("title", section.get("title"));
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
    },
  })
);


storybase.collections.Stories = Backbone.Collection.extend({
    model: storybase.models.Story,

    url: function() {
      return storybase.globals.API_ROOT + 'stories';
    }
});

storybase.models.Section = Backbone.Model.extend(
  _.extend({}, storybase.models.TastypieMixin, {
    idAttribute: "section_id",

    initialize: function() {
      this.assets = new storybase.collections.SectionAssets;
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
      return storybase.globals.API_ROOT + 'sections';
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

storybase.collections.Sections = Backbone.Collection.extend(
  _.extend({}, storybase.collections.TastypieMixin, {
    model: storybase.models.Section,

    url: storybase.globals.API_ROOT + 'sections/',

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

storybase.models.StoryRelation = Backbone.Model.extend({
  idAttribute: "relation_id"
});

storybase.collections.StoryRelations = storybase.collections.SaveableCollection.extend(
  _.extend({}, storybase.collections.TastypieMixin, {
    model: storybase.models.StoryRelation,

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
      return storybase.collections.SaveableCollection.prototype.save.call(this, options);
    },

    setStory: function(story) {
      this._story = story;
    },

    url: function() {
      return _.result(this._story, 'url') + 'related/';
    }
  })
);

storybase.models.Asset = Backbone.Model.extend(
  _.extend({}, storybase.models.TastypieMixin, {
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
     * This is done witha function instead of declaring an object because
     * the fields differ depending on the type of asset.
     */
    schema: function() {
      if (!_.isUndefined(storybase.forms)) {
        var schema = {
          title: {title: gettext("Title"), type: 'Text'},
          url: {title: gettext("URL"), type: 'Text', validators: ['url']},
          image: {title: gettext("Image file"), type: storybase.forms.File},
          body: {title: gettext("Body"), type: 'TextArea'},
          //caption: {title: gettext("Caption"), type: 'TextArea'},
          attribution: {title: gettext("Attribution"), type: 'TextArea'},
          source_url: {title: gettext("Source URL"), type: 'Text', validators: ['url']}
        };
        var type = this.get('type');
        var self = this;
        // Remove fields that aren't relevant for a particular type
        _.each(schema, function(field, name, schema) {
          if (!this.formFieldVisible(name, type)) {
            delete schema[name];
          }
        }, this);
        if (!this.isNew()) {
          // For a saved model, only show the fields that have a value set.
          _.each(['image', 'url', 'body'], function(field) {
            var value = self.get(field);
            if (!value) {
              delete schema[field];
            }
          });
        }

        return schema;
      }
    },

    idAttribute: "asset_id",

    urlRoot: function() {
      return storybase.globals.API_ROOT + 'assets/'
    },

    /**
     * Validate the model attributes
     *
     * Make sure that only one of the content attributes is set to a truthy
     * value.
     */
    validate: function(attrs) {
      var contentAttrNames = ['body', 'image', 'url'];
      var found = [];
      _.each(contentAttrNames, function(attrName) {
        if (_.has(attrs, attrName) && attrs[attrName]) {
          found.push(attrName);
        }
      });
      if (found.length > 1) {
        return "You must specify only one of the following values " + found.join(', ');
      }
    }
  })
);

storybase.collections.Assets = Backbone.Collection.extend(
  _.extend({}, storybase.collections.TastypieMixin, {
    model: storybase.models.Asset
  })
);

storybase.collections.SectionAssets = storybase.collections.Assets.extend({
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

storybase.collections.FeaturedAssets = storybase.collections.SaveableCollection.extend(
  _.extend({}, storybase.collections.TastypieMixin, {
    model: storybase.models.Asset,

    initialize: function(models, options) {
      if (!_.isUndefined(options)) {
        this.setStory(options.story);
      }
    },

    save: function(options) {
      return storybase.collections.SaveableCollection.prototype.save.call(this, options);
    },

    setStory: function(story) {
      this._story = story;
    },

    url: function() {
      return storybase.globals.API_ROOT + 'assets/stories/' + this._story.id + '/featured/';
    }
  })
);

storybase.models.Tag = Backbone.Model.extend({
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

storybase.collections.Tags = Backbone.Collection.extend(
  _.extend({}, storybase.collections.TastypieMixin, {
    model: storybase.models.Tag,

    initialize: function(models, options) {
      this._story = _.isUndefined(options.story) ? null : options.story;
    },

    url: function() {
      var url = storybase.globals.API_ROOT + 'tags/';
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
