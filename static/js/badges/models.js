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

  var StoryBadges = function(story) {
    this.story = story;
    this.storyId = this.story.id;
    this.storyUri = storybase.API_ROOT + 'stories/' + this.storyId + '/';
  }

  StoryBadges.prototype.add = function(badge) {
    var stories = badge.get('stories');
    stories.push(this.storyUri);

    badge.save({stories: stories}, {patch: true});

    return this;
  }

  StoryBadges.prototype.remove = function(badge) {

    var stories = _.filter(badge.get('stories'), function(s) {
      return s != this.storyUri;
    }, this);

    badge.save({stories: stories}, {patch: true});

    return this;
  }

  var Story = storybase.models.Story;

  storybase.badges.models.Badge = Badge;
  storybase.badges.collections.Badges = Badges;
  storybase.badges.models.StoryBadges = StoryBadges;

})(_, Backbone, storybase);
