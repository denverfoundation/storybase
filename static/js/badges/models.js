;(function(_, Backbone, storybase) {

  if (_.isUndefined(storybase.badges.models)) {
    storybase.badges.models = {};
  }

  if (_.isUndefined(storybase.badges.collections)) {
    storybase.badges.collections = {};
  }

  var Badge = Backbone.Model.extend({

  });

  var Badges = Backbone.Collection.extend(
    _.extend({}, storybase.collections.TastypieMixin, {
      url: function() {
        return storybase.API_ROOT + 'badges/';
      },
      model: Badge
    })
  );

  var StoryBadges = Badges.extend({
    initialize: function(options) {
      this.story = options.story;
      this.storyUri = storybase.API_ROOT + 'stories/' + this.story.id + '/';
    },
    parse: function(response) {
      var objects = response.objects;

      var storyBadges = _.filter(objects, function(b) {
        return _.contains(b.stories, this.storyUri);
      }, this);

      return storyBadges;
    },
    addBadge: function(b) {
      var stories = b.get('stories');
      stories.push(this.storyUri);
      this._saveBadge(b, stories);

      return this;

    },
    removeBadge: function(b) {
      var stories = _.filter(b.get('stories'), function(s) {
        return s != this.storyUri;
      }, this);

      this._saveBadge(b, stories);

      return this;

    },
    _saveBadge: function(b, stories) {
      b.save({stories: stories}, {patch: true});
    }
  });

  storybase.badges.models.Badge = Badge;
  storybase.badges.collections.Badges = Badges;
  storybase.badges.models.StoryBadges = StoryBadges;

})(_, Backbone, storybase);
