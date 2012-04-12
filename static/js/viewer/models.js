/**
 * Models for the story viewer Backbone application
 */
Namespace('storybase.viewer');

storybase.viewer.models.Story = Backbone.Model.extend({
  idAttribute: "story_id"
});

storybase.viewer.models.Section = Backbone.Model.extend({
  idAttribute: "section_id",

  populateChildren: function() {
    var $this = this;
    this.children = this.get('children').map(function(childId) {
      return $this.collection.get(childId);
    });
    return this;
  },

  title: function() {
    return this.get("title");
  }
});

storybase.viewer.collections.Sections = Backbone.Collection.extend({
    model: storybase.viewer.models.Section
});
 
