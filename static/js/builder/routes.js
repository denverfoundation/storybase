Namespace('storybase.builder.routers');
storybase.builder.routers.Router = Backbone.Router.extend({
  routes: {
    "": "debug",
    ":id/": "selectStep",
    ":id/:step/": "selectStep",
    ":id/:step/:substep/": "selectStep",
  },

  initialize: function(options) {
    this.dispatcher = options.dispatcher;
    this.dispatcher.on("navigate", this.navigate, this);
  },

  debug: function() {
    this.dispatcher.trigger('select:workflowstep', 'selecttemplate');
  },

  selectStep: function(id, step, subStep) {
    if (_.isUndefined(step)) {
      step = 'build';
    }
    console.debug('Router matched ' + step + '/' + subStep);
    this.dispatcher.trigger('select:workflowstep', step, subStep);
  }
});
