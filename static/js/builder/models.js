Namespace('storybase.builder.models');
Namespace('storybase.builder.collections');

storybase.builder.models.StoryTemplate = Backbone.Model.extend({
  idAttribute: "template_id",

  /**
   * Retrive the story ID for the story that provides the structure for 
   * the model.
   */
  getStoryId: function() {
    var uriParts = this.get('story').split('/');
    return uriParts[uriParts.length - 2];
  },

  /**
   * Get an instance of a Story model for the story that provides
   * the structure for the model.
   */
  getStory: function(options) {
    var story = new storybase.models.Story({ story_id: this.getStoryId() }); 
    story.fetch({
      success: function(model, response) {
        if (_.isFunction(options.success)) {
          options.success(model);
        }
      },
      error: function(model, response) {
        if (_.isFunction(options.error)) {
          options.error(model, response);
        }
      }
    });
    return story;
  }
});

storybase.builder.collections.StoryTemplates = Backbone.Collection.extend({
  model: storybase.builder.models.StoryTemplate,

  parse: function(response) {
    return response.objects;
  }
});

storybase.builder.collections.ContainerTemplates = Backbone.Collection.extend(
  _.extend({}, storybase.collections.TastypieMixin, {
    initialize: function(models, options) {
      this._template = _.isUndefined(options) ? null : options.template;
    },

    setTemplate: function(template) {
      this._template = template;
    },

    url: function() {
      var url = storybase.globals.API_ROOT + 'stories/containertemplates/';
      if (this._template) {
        url = url + 'templates/' + this._template.id + '/';
      }
      return url;
    }
  })
);
