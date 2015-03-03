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

  // TODO: make this into a mixin
  var FilteredBadges = Badges.extend({
    parse: function(response) {
      var objects = response.objects;

      var storyBadges = _.filter(objects, function(b) {
        return this.predicate(b);
      }, this);

      return storyBadges;


    }

  });

  var UserBadges = FilteredBadges.extend({
    initialize: function(options) {
      this.allowed = options.allowed;
    },
    predicate: function(badge) {
      return _.contains(this.allowed, badge.id);
    }
  });

  var StoryBadges = FilteredBadges.extend({
    initialize: function(options) {
      this.story = options.story;
      this.storyUri = storybase.API_ROOT + 'stories/' + this.story.id + '/';
    },
    predicate: function(badge) {
      return _.contains(badge.stories, this.storyUri);
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
  storybase.badges.collections.UserBadges = UserBadges;
  storybase.badges.collections.StoryBadges = StoryBadges;

})(_, Backbone, storybase);
