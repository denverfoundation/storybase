/**
 * Routes for the story viewer Backbone application.
 */
;(function(_, Backbone, storybase) {
  if (_.isUndefined(storybase.viewer.routers)) {
    storybase.viewer.routers = {};
  }
  var Routers = storybase.viewer.routers;

  Routers.Router = Backbone.Router.extend({
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
  });
})(_, Backbone, storybase);
