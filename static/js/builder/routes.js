Namespace('storybase.builder.routers');
storybase.builder.routers.Router = Backbone.Router.extend({
  routes: {
    ":id/": "selectStep",
    ":id/:step/": "selectStep"
  },

  initialize: function(options) {
    this.dispatcher = options.dispatcher;
    this.dispatcher.on("navigate", this.navigate, this);
  },

  selectStep: function(id, step) {
    if (_.isUndefined(step)) {
      step = 'build';
    }
    this.dispatcher.trigger('select:workflowstep', step);
  }
   
});
