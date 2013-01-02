Namespace('storybase.builder.routers');
Namespace.use('storybase.utils.hasAnalytics');

storybase.builder.routers.Router = Backbone.Router.extend({
  initialize: function(options) {
    this.dispatcher = options.dispatcher;
    this.hasStory = options.hasStory;
    this.hasTemplate = options.hasTemplate;
    this.storyReady = this.hasStory;
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
    this.dispatcher.on("ready:story", this.setStoryReady, this);
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
      if (!this.storyReady) {
        // If we're attempting to load an existing story, reload the page
        // in the browser with an un-hashed story ID to force the bootstrapping
        // of the views. If this is the initial save of a new story, don't
        // reload. 
        window.location.replace(url);
      }
    }

    this.selectStep('build');
  },

  selectTemplate: function() {
    this.selectStep('selecttemplate');
  },

  selectIdStep: function(id, step, subStep) {
    this.selectStep(step, subStep);
  },

  /**
   * Signal handler for ready:story signal.
   *
   * Toggles the this.storyReady flag to true.
   */
  setStoryReady: function(story) {
    this.storyReady = true;
  }
});
