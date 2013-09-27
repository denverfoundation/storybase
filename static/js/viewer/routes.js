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
    }
  });
})(_, Backbone, storybase);
