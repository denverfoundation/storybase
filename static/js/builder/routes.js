Namespace('storybase.builder.routers');
Namespace.use('storybase.utils.hasAnalytics');

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

  build: function(id) {
    var url;
    if (id) {
      // The page was loaded with an id via a hash, so the views haven't
      // been bootstrapped.  Force a page refresh so that the views will
      // be properly bootstrapped.
      if (hasAnalytics()) {
        _gaq.push(['_trackEvent', 'Routes', 'Page load with hashed story ID']);
      }
      if (window.location.hash) {
        // Remove the hash from the URL. The server will generate the 
        // correct content for the workflow step when requested directly
        url = window.location.href.replace('#', '');
      }
      else {
        // No hash, likely because the browser supports the History API and
        // Backbone has already updated the location to be hash-less
        url = window.location.href;
      }
      window.location.replace(url);
    }
    else {
      this.selectStep('build');
    }
  },

  selectTemplate: function() {
    this.selectStep('selecttemplate');
  },

  selectIdStep: function(id, step, subStep) {
    this.selectStep(step, subStep);
  }
});
