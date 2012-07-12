Namespace('storybase.builder.routers');
storybase.builder.routers.Router = Backbone.Router.extend({
  routes: {
    "story/:id": "story",
    "selecttemplate": "selecttemplate" 
  },

  initialize: function(options) {
    this.dispatcher = options.dispatcher;
    this.dispatcher.on("navigate", this.navigate, this);
    this.dispatcher.on("navigate", this.debug, this);
  },

  story: function(id) {
    this.dispatcher.trigger("select:story");
  },

  debug: function(fragment, options) {
    this.navigate(fragment);
  },

  selecttemplate: function() {
  }
});
