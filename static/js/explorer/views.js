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
    this.filterView.render();
    console.debug(this.filterView.el);
    this.$el.append(this.filterView.el);
  }
});

storybase.explorer.views.Filters = Backbone.View.extend({
  tagName: 'div',

  id: 'filters',

  render: function() {
    var context = {};
    context.topics = this.options.topics;
    context.organizations = this.options.organizations;
    context.projects = this.options.projects;
    context.languages = this.options.languages;
    context.gettext = function() {
      return function(text) {
        return gettext(text);
      }
    };
    this.$el.html(ich.filtersTemplate(context));
  }
});
