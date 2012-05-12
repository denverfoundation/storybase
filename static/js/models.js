/* Models shared across multiple storybase apps */
Namespace('storybase.models');

storybase.models.Story = Backbone.Model.extend({
  idAttribute: "story_id"
});
