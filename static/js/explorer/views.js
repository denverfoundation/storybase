/**
 * Views for the story explorer Backbone application
 */
Namespace('storybase.explorer');

storybase.explorer.views.Filters = Backbone.View.extend({
  el: $('#filters'),

  render: function(options) {
    var context;
    // Check to see if this method was passed extra template context
    // The main reason for this is to be able to define translated strings
    // in the template rather than the view.
    if (typeof options === "undefined" || 
        typeof options.extraContext === "undefined") {
      context = {};
    }
    else {
      context = options.extraContext;
    }
    this.$el.html(ich.filtersTemplate(context));
  }
});
