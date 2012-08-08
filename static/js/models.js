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

storybase.models.Story = Backbone.Model.extend(
  _.extend({}, storybase.models.TastypieMixin, {
    idAttribute: "story_id",

    urlRoot: function() {
      return storybase.globals.API_ROOT + 'stories';
    },

    defaults: {
      'title': '',
      'byline': '',
      'summary': ''
    },

    initialize: function(options) {
      this.sections = new storybase.collections.Sections;
      this.unusedAssets = new storybase.collections.Assets;
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
      }
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
     * Save all the sections of the story
     */
    saveSections: function(options) {
      this.sections.each(function(section) {
        section.save();
      });
    }
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

    populateChildren: function() {
      var $this = this;
      this.children = this.get('children').map(function(childId) {
        return $this.collection.get(childId).populateChildren();
      });
      return this;
    },

    title: function() {
      return this.get("title");
    }
  })
);

storybase.collections.Sections = Backbone.Collection.extend(
  _.extend({}, storybase.collections.TastypieMixin, {
    model: storybase.models.Section,

    url: storybase.globals.API_ROOT + 'sections/',

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
  })
);

storybase.models.Asset = Backbone.Model.extend(
  _.extend({}, storybase.models.TastypieMixin, {
    showUrl: {
      'image': true,
      'audio': true,
      'video': true,
      'map': true,
      'table': true,
    },

    showImage: {
      'image': true,
      'map': true
    },

    showBody: {
      'text': true,
      'quotation': true,
      'map': true,
      'table': true,
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
          url: {type: 'Text', validators: ['url']},
          image: {type: storybase.forms.File},
          body: {type: 'TextArea'},
          caption: {type: 'TextArea'}
        };
        var type = this.get('type');
        var self = this;
        // Remove fields that aren't relevant for a particular type
        if (!(_.has(this.showBody, type))) {
          delete schema.body;
        }
        if (!(_.has(this.showImage, type))) {
          delete schema.image;
        }
        if (!(_.has(this.showUrl, type))) {
          delete schema.url;
        }
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
