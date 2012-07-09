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

  /**
   * Retrieve a collection of sections of the story
   */
  fetchSections: function(options) {
    if (_.isUndefined(this.sections)) {
      this.sections = new storybase.collections.Sections({
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
  }
});

storybase.collections.Sections = Backbone.Collection.extend({
    model: storybase.models.Section,

    initialize: function(options) {
      if (!_.isUndefined(options)) {
        if (!_.isUndefined(options.story)) {
          this.story = options.story;
        }
      }
    },

    url: function() {
      if (!_.isUndefined(this.story)) {
        return this.story.url() + 'sections/';
      }
      else {
        return '/api/0.1/sections/';
      }
    },

    parse: function(response) {
      return response.objects;
    }
});
