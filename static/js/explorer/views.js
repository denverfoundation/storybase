/**
 * Views for the story explorer Backbone application
 */
Namespace('storybase.explorer');

storybase.explorer.views.Filters = Backbone.View.extend({
  el: $('#filters'),

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
