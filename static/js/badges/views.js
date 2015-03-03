;(function(_, Backbone, storybase) {

  if (_.isUndefined(storybase.badges.views)) {
    storybase.badges.views = {};
  }

  var BadgeView = Backbone.View.extend({
    template: _.template($('#badge-template').html()),
    tagName: 'span',
    render: function() {
      this.$el.html(this.template(this.model.attributes));
      return this;
    }
  });

  var BadgesView = Backbone.View.extend({
    render: function() {

      this.$el.html('');

      this.collection.each(function(badge){
        var bv = new BadgeView({model: badge});
        this.$el.append(bv.render().el);

      }, this);

      return this;
    }

  });

  storybase.badges.views.BadgeView = BadgeView;
  storybase.badges.views.BadgesView = BadgesView;

})(_, Backbone, storybase);
