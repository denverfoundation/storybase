;(function(_, Backbone, storybase) {
  if (_.isUndefined(storybase.builder.models)) {
    storybase.builder.models = {};
  }
  var Models = storybase.builder.models;

  if (_.isUndefined(storybase.builder.collections)) {
    storybase.builder.collections = {};
  }
  var Collections = storybase.builder.collections;

  var TastypieMixin = storybase.collections.TastyPieMixin;

  var StoryTemplate = Models.StoryTemplate = Backbone.Model.extend({
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

  Collections.StoryTemplates = Backbone.Collection.extend({
    model: StoryTemplate,

    parse: function(response) {
      return response.objects;
    }
  });

  Collections.ContainerTemplates = Backbone.Collection.extend(
    _.extend({}, TastypieMixin, {
      initialize: function(models, options) {
        this._template = _.isUndefined(options) ? null : options.template;
      },

      setTemplate: function(template) {
        this._template = template;
      },

      url: function() {
        var url = storybase.API_ROOT + 'stories/containertemplates/';
        if (this._template) {
          url = url + 'templates/' + this._template.id + '/';
        }
        return url;
      }
    })
  );
})(_, Backbone, storybase);
