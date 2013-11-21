;(function(Backbone, storybase) {
  var hasAnalytics = storybase.utils.hasAnalytics;

  if (_.isUndefined(storybase.builder.routers)) {
    storybase.builder.routers = {};
  }
  var Routers = storybase.builder.routers;

  Routers.Router = Backbone.Router.extend({
    initialize: function(options) {
      this.dispatcher = options.dispatcher;
      this.hasStory = options.hasStory;
      this.hasTemplate = options.hasTemplate;
      // Define the routes dynamically instead of a declaring
      // a routes property because the routing changes
      // depending on whether we're creating a new story
      // or editing an existing story.
      //
      // Remember that routes added later take precedence over
      // routes added earlier.
      if (this.hasStory) {
        // Editing an existing story
        this.route("", "build");
        this.route(":step/", "selectStep");
        this.route(":step/:substep/", "selectStep");
      }
      else {
        // Creating a new story

        // Create routes for the workflow steps once the story is
        // saved and an Id is assigned
        this.route(":id/", "build");
        this.route(":id/:step/", "selectIdStep");
        this.route(":id/:step/:substep/", "selectIdStep");

        if (this.hasTemplate) {
          // Template is already selected.  Default route points to
          // build workflow step
          this.route("", "build");
        }
        else {
          // A template hasn't been selected.  Default route points
          // to template selection workflow step
          this.route("", "selectTemplate");
          // The info workflow step should be accessible before the
          // story is saved
          this.route("info/", "info");
        }
      }
      this.dispatcher.on("navigate", this.navigate, this);
      this.dispatcher.once("save:story", this.setHasStory, this);
      this.dispatcher.once("select:template", this.setHasTemplate, this);
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
      if (!this.hasStory && step != 'build' && step != 'selecttemplate' && step != 'info') {
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

    info: function() {
      this.selectStep('info');
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
    },

    setHasTemplate: function() {
      this.hasTemplate = true;
      // Default route should be to build step, not template selection
      this.route("", "build");
    }

  });
})(Backbone, storybase);
