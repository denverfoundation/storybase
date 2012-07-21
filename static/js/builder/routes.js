Namespace('storybase.builder.routers');
storybase.builder.routers.Router = Backbone.Router.extend({
  routes: {
    ":id/": "selectStep",
    ":id/:step/": "selectStep",
    ":id/:step/:substep/": "selectStep",
  },

  initialize: function(options) {
    this.dispatcher = options.dispatcher;
    this.dispatcher.on("navigate", this.navigate, this);
  },

  selectStep: function(id, step, subStep) {
    if (id == 'en' || id == 'es') {
      // Workaround for internationalized URLs
      id = step;
      step = undefined; 
      subStep = undefined;
    }
    if (_.isUndefined(step)) {
      step = 'build';
    }
    this.dispatcher.trigger('select:workflowstep', step, subStep);
  }
});
