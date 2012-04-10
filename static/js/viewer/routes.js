/**
 * Routes for the story viewer Backbone application.
 */
Namespace('storybase.viewer');
storybase.viewer.routers.Router = Backbone.Router.extend({
  routes: {
    "sections/:id": "section"
  },

  initialize: function(options) {
    this.view = options.view;
  },

  section: function(id) {
    this.view.setSectionById(id);
  }
})
