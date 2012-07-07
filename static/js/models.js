/* Models shared across multiple storybase apps */
Namespace('storybase.models');
Namespace('storybase.collections');

storybase.models.Story = Backbone.Model.extend({
  idAttribute: "story_id",

  urlRoot: function() {
    return '/api/0.1/stories'; 
  },

  url: function() {
    return this.urlRoot() + "/" + this.id + "/";
  },
});

storybase.collections.Stories = Backbone.Collection.extend({
    model: storybase.models.Story,

    url: function() {
      return '/api/0.1/stories';
    }
});
