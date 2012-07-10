/* Models shared across multiple storybase apps */
Namespace('storybase.models');
Namespace('storybase.collections');

storybase.models.Story = Backbone.Model.extend({
  idAttribute: "story_id",

  urlRoot: function() {
    return '/api/0.1/stories';
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
    if (_.isUndefined(this.sections)) {
      this.sections = new storybase.collections.Sections([], {
        story: this
      });
    }
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
      return '/api/0.1/stories';
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

    url: '/api/0.1/sections/', 

    parse: function(response) {
      return response.objects;
    }
});
