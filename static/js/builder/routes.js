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
    // TODO: Figure out the best workaround for internationalized URLs
    if (id === 'en' || id === 'es') {
      // Workaround for internationalized URLs
      var chunks = [step, subStep];
      if (chunks[0] === 'build') {
        if (_.isUndefined(chunks[1])) {
          // /en/build/
          id = undefined;
          step = undefined;
        }
        else {
          // /en/build/357c5885c4e844cb8a4cd4eebe912a1c/
          id = chunks[1];
          step = chunks[0]; // build
        }
        subStep = undefined;
      }
    }
    else {
      if (_.isUndefined(step) && !_.isUndefined(id)) {
        step = 'build';
      }
    }
    if (!_.isUndefined(step)) {
      this.dispatcher.trigger('select:workflowstep', step, subStep);
    }
  }
});
