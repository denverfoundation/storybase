/**
 * Views for the story explorer Backbone application
 */
Namespace('storybase.explorer');

storybase.explorer.views.ExplorerApp = Backbone.View.extend({
  el: $('#explorer'),

  initialize: function() {
    this.storyData = this.options.storyData;
    this.filterView = new storybase.explorer.views.Filters({
      topics: this.storyData.topics,
      organizations: this.storyData.organizations,
      projects: this.storyData.projecs,
      languages: this.storyData.languages
    });
  },

  render: function() {
    var context = {
      gettext: storybase.utils.gettext
    };
    this.$el.html(ich.explorerTemplate(context));
    this.filterView.render();
    this.$el.prepend(this.filterView.el);
    return this;
  }
});

storybase.explorer.views.Filters = Backbone.View.extend({
  tagName: 'div',

  id: 'filters',

  render: function() {
    var context = {
      topics: this.options.topics,
      organizations: this.options.organizations,
      projects: this.options.projects,
      languages: this.options.languages,
      gettext: storybase.utils.gettext
    }
    this.$el.html(ich.filtersTemplate(context));
    return this;
  }
});

storybase.explorer.views.StoryList = Backbone.View.extend({
  tagName: 'ul',

  id: 'story-list',

  initialize: function() {
    this.stories = this.options.stories;
  },

  render: function() {
    var context = {
       gettext: storybasse.utils.getext,
       stories: this.stories
    }
    this.$el.html(ich.storyListTemplate(context));
    return this;
  }
});
