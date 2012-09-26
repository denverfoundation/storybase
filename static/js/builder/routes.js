Namespace('storybase.builder.routers');
storybase.builder.routers.Router = Backbone.Router.extend({
  initialize: function(options) {
    this.dispatcher = options.dispatcher;
    this.hasStory = options.hasStory;
    this.hasTemplate = options.hasTemplate;
    // Define the routes dynamically instead of a declaring
    // a rotues property because the routing changes
    // depending on whether we're creating a new story
    // or editing an existing story
    if (this.hasStory) {
      // Editing an existing story
      this.route("", "build");
      this.route(":step/", "selectStep");
      this.route(":step/:substep/", "selectStep");
    }
    else {
      // Creating a new story
      if (this.hasTemplate) {
        this.route("", "build");
      }
      else {
        this.route("", "selectTemplate");
      }
      this.route(":id/", "build");
      this.route(":id/:step/", "selectIdStep");
      this.route(":id/:step/:substep/", "selectIdStep");
    }
    this.dispatcher.on("navigate", this.navigate, this);
  },

  selectStep: function(step, subStep) {
    console.debug('Router matched ' + step + '/' + subStep);
    this.dispatcher.trigger('select:workflowstep', step, subStep);
  },

  build: function() {
    this.selectStep('build');
  },

  selectTemplate: function() {
    this.selectStep('selecttemplate');
  },

  selectIdStep: function(id, step, subStep) {
    this.selectStep(step, subStep);
  }
});
