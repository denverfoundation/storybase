;(function(_, Backbone, storybase) {

  if (_.isUndefined(storybase.badges.models)) {
    storybase.badges.models = {};
  }

  if (_.isUndefined(storybase.badges.collections)) {
    storybase.badges.collections = {};
  }

  var Badge = Backbone.Model.extend({

  });

  storybase.badges.models.Badge = Badge;

})(_, Backbone, storybase);
