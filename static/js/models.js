/* Models shared across multiple storybase apps */
Namespace('storybase.globals');
Namespace('storybase.models');
Namespace('storybase.collections');

storybase.models.Story = Backbone.Model.extend({
  idAttribute: "story_id",

  urlRoot: function() {
    return storybase.globals.API_ROOT + 'stories';
  },

  url: function() {
    var url = this.urlRoot();
    if (!this.isNew()) {
      url = url + "/" + this.id;
    }
    url = url + "/";
    return url;
  },

  initialize: function(options) {
    this.sections = new storybase.collections.Sections;
    this.setSectionsUrl();
    this.on("change", this.setSectionsUrl, this);
  },

  setSectionsUrl: function() {
    if (!this.isNew()) {
      this.sections.url = this.url() + 'sections/';
    }
  },

  /**
   * Retrieve a collection of sections of the story
   */
  fetchSections: function(options) {
    this.sections.fetch({
      success: function(collection, response) {
        if (_.isFunction(options.success)) {
          options.success(collection);
        }
      },
      error: function(collection, response) {
        if (_.isFunction(options.error)) {
          options.error(collection, response);
        }
      }
    });
    return this.sections;
  },

  /**
   * Save all the sections of the story
   */
  saveSections: function(options) {
    this.sections.each(function(section) {
      section.save();
    });
  }
});

storybase.collections.Stories = Backbone.Collection.extend({
    model: storybase.models.Story,

    url: function() {
      return storybase.globals.API_ROOT + 'stories';
    }
});

storybase.models.Section = Backbone.Model.extend({
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
  },

  url: function() {
    var url = Backbone.Model.prototype.url.call(this);
    if (url.charAt(url.length - 1) != '/') {
      url = url + '/';
    }
    return url;
  }
});

storybase.collections.Sections = Backbone.Collection.extend({
    model: storybase.models.Section,

    url: storybase.globals.API_ROOT + 'sections/', 

    parse: function(response) {
      return response.objects;
    }
});

storybase.models.Asset = Backbone.Model.extend({
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
    'quotation': true
  },

  /**
   * Build the schema for backbone-forms
   *
   * This is done witha function instead of declaring an object because
   * the fields differ depending on the type of asset.
   */
  schema: function() {
    var schema = {
      body: 'TextArea',
      url: {type: 'Text', validators: ['url']},
      image: {type: storybase.forms.File}
    };
    var type = this.get('type');
    if (!(_.has(this.showBody, type))) {
      delete schema.body;
    }
    if (!(_.has(this.showImage, type))) {
      delete schema.image;
    }
    if (!(_.has(this.showUrl, type))) {
      delete schema.url;
    }

    return schema;
  },

  idAttribute: "asset_id",

  url: function() {
    var url = Backbone.Model.prototype.url.call(this);
    if (url.charAt(url.length - 1) != '/') {
      url = url + '/';
    }
    return url;
  },

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
      // TODO: Translate this
      return "You must specify only one of the following values " + found.join(', ');
    }
  }
});

storybase.collections.Assets = Backbone.Collection.extend({
    model: storybase.models.Asset
});

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
