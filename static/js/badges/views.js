;(function(_, Backbone, storybase) {

  if (_.isUndefined(storybase.badges.views)) {
    storybase.badges.views = {};
  }

  var BadgeView = Backbone.View.extend({
    template: _.template($('#badge-template').html()),
    tagName: 'span',
    events: {
      'click .badge': 'clicked'
    },
    clicked: function(event) {
      this.parent.clickedSubView(event, this);
    },
    render: function() {
      this.$el.html(this.template(this.model.attributes)).children('a').tooltipster({
          position: 'bottom',
          offsetY: -12
        });
      return this;
    }
  });

  var BadgesView = Backbone.View.extend({
    SubView: BadgeView,
    render: function() {
      this.$el.html('');

      this.collection.each(function(badge){
        var bv = new this.SubView({model: badge});
        bv.parent = this;
        this.$el.append(bv.render().el);

      }, this);

      return this;
    },
    clickedSubView: function(event, view) {
        $('#show-badge').bPopup({
            modalClose: true,
            opacity: 0.6,
            positionStyle: 'fixed'
        })
        .find('#show-badge-heading').html(view.model.get('name'))
        .end()
        .find('#show-badge-body').html(view.model.get('description'));
    }
  });

  var StoryBadgesEditorView = BadgesView.extend({
    initialize: function(options) {
      this.userBadges = options.userBadges;
      this.storyBadges = options.storyBadges;
      this.badgesView = options.badgesView;
    },
    clickedSubView: function(event, view) {
      this.badgesView.render();
      view.remove();
    },
    SubView: BadgeView,
  });

  var RemoveBadgesView = StoryBadgesEditorView.extend({
    clickedSubView: function(event, view) {
      this.storyBadges.removeBadge(view.model);
      StoryBadgesEditorView.prototype.clickedSubView.call(this, event, view);
    }
  });

  var AddBadgesView = StoryBadgesEditorView.extend({
    clickedSubView: function(event, view) {
      this.storyBadges.addBadge(view.model);
      StoryBadgesEditorView.prototype.clickedSubView.call(this, event, view);
    }
  });


  storybase.badges.views.BadgeView = BadgeView;
  storybase.badges.views.BadgesView = BadgesView;

  storybase.badges.views.StoryBadgesEditorView = StoryBadgesEditorView;
  storybase.badges.views.AddBadgesView = AddBadgesView;
  storybase.badges.views.RemoveBadgesView = RemoveBadgesView;

})(_, Backbone, storybase);
