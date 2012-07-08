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
    model: storybase.models.Section
});
 
