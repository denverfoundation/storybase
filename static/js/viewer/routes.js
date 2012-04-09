/**
 * Routes for the story viewer Backbone application.
 */
Namespace('storybase.viewer');
var storybase.viewer.Router = Backbone.Router.extend({
  routes: {
    "section/:id": "section"
  }
});
