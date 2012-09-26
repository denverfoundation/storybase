/**
 * Routes for the story viewer Backbone application.
 */
Namespace('storybase.viewer');
storybase.viewer.routers.Router = Backbone.Router.extend({
  routes: {
    "sections/:id": "section",
    "connected-stories/:id": "connectedStory",
  },

  initialize: function(options) {
    this.view = options.view;
  },

  section: function(id) {
    this.view.setSectionById(id);
  },

  connectedStory: function(id) {
    this.view.showConnectedStory(id);
  }
})
