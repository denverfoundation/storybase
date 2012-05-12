/* Models shared across multiple storybase apps */
Namespace('storybase.models');
Namespace('storybase.collections');

storybase.models.Story = Backbone.Model.extend({
  idAttribute: "story_id"
});

storybase.collections.Stories = Backbone.Collection.extend({
    model: storybase.models.Story
});
