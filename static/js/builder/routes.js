Namespace('storybase.builder.routers');
storybase.builder.routers.Router = Backbone.Router.extend({
  routes: {
    "": "selectInitialStep",
    ":id/": "selectStep",
    ":id/:step/": "selectStep",
    ":id/:step/:substep/": "selectStep",
  },

  initialize: function(options) {
    this.dispatcher = options.dispatcher;
    this.dispatcher.on("navigate", this.navigate, this);
  },

  selectInitialStep: function() {
    this.selectStep(undefined, 'selecttemplate');
  },

  selectStep: function(id, step, subStep) {
    if (_.isUndefined(step)) {
      step = 'build';
    }
    console.debug('Router matched ' + step + '/' + subStep);
    this.dispatcher.trigger('select:workflowstep', step, subStep);
  }
});
