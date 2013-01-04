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
    this.dispatcher.on("save:story", this.setHasStory, this);
  },

  /**
   * Handle hashed story IDs in the URL, reloading the page if neccessary 
   *
   * @param {Boolean} reload Should the page be reloaded in the browser?
   *
   * Backbone's router will use hashed URL paths in browsers that don't
   * support the History API. This causes problems if a user accesses one
   * of these URLs directly, such as from a bookmark, because the Django
   * view doesn't know to bootstrap the backbone views.  To work around
   * this, we force a page reload.
   */
  handleHashedId: function(reload) {
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
    if (reload) {
      // If we're attempting to load an existing story, reload the page
      // in the browser with an un-hashed story ID to force the bootstrapping
      // of the views. If this is the initial save of a new story, don't
      // reload. 
      window.location.replace(url);
    }
  },

  selectStep: function(step, subStep) {
    console.debug('Router matched ' + step + '/' + subStep);
    if (!this.hasStory && step != 'build' && step != 'selecttemplate') {
      this.handleHashedId(!this.hasStory);
    }
    this.dispatcher.trigger('select:workflowstep', step, subStep);
  },

  build: function(id) {
    var url;
    if (id) {
      this.handleHashedId(!this.hasStory);
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
   * Signal handler for the save:story signal.
   *
   * Toggles the this.hasStory flag to true.
   */
  setHasStory: function(story) {
    this.hasStory = true;
  }
});
