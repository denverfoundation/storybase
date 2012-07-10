Namespace('storybase.builder.views');

/**
 * Master view for the story builder
 *
 * Dispatches to sub-views.
 */
storybase.builder.views.AppView = Backbone.View.extend({
  initialize: function() {
    this.dispatcher = this.options.dispatcher;

    // The currently active step of the story building process
    // TODO: Define all the steps
    this.activeStep = 'selectTemplate';

    this.navView = new storybase.builder.views.NavigationView({
      el: this.$('#builder-nav'),
      dispatcher: this.dispatcher
    });

    // Store subviews in an object keyed with values of this.activeStep
    this.subviews = {
      selectTemplate: new storybase.builder.views.SelectStoryTemplateView({
        dispatcher: this.dispatcher,
        collection: this.options.storyTemplates
      }),
      build: new storybase.builder.views.BuilderView({
        dispatcher: this.dispatcher
      })
    };

    this.initializeEvents();
  },

  /**
   * Bind callbacks for custom events
   */
  initializeEvents: function() {
    this.dispatcher.on("select:template", this.setTemplate, this);
  },

  /**
   * Set the template and move to the next step of the workflow
   */
  setTemplate: function(template) {
    this.activeTemplate = template;
    this.updateStep('build');
  },

  /**
   * Set the active step of the workflow and re-render the view
   */
  updateStep: function(step) {
    this.activeStep = step;
    this.render();
  },

  /**
   * Get the sub-view for the currently active step
   */
  getActiveView: function() {
    return this.subviews[this.activeStep];
  },

  render: function() {
    var activeView = this.getActiveView();
    this.$('#app').html(activeView.render().$el);
    this.navView.render();
    return this;
  }
});

/**
 * Story builder navigation menu
 */
storybase.builder.views.NavigationView = Backbone.View.extend({
  templateSource: $('#navigation-template').html(),

  events: {
    "click .save": "save"
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
  },

  render: function() {
    var context = {};
    this.$el.html(this.template(context));
    return this;
  },

  /**
   * Event handler for clicking the save link
   */
  save: function(e) {
    this.dispatcher.trigger("save:story");
    e.preventDefault();
  }
});

/**
 * Story template selector
 */
storybase.builder.views.SelectStoryTemplateView = Backbone.View.extend({
  tagName: 'ul',
 
  // TODO: Remove row from classes when we apply real styles.  The row
  // class is just used for my bootstrap layout based on the 1140 grid
  // system
  className: 'story-templates row',

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    _.bindAll(this, 'addTemplateEntry');
  },

  addTemplateEntry: function(template) {
      var view = new storybase.builder.views.StoryTemplateView({
        dispatcher: this.dispatcher,
        model: template
      });
      this.$el.append(view.render().el);
  },

  render: function() {
    this.collection.each(this.addTemplateEntry);
    return this;
  }
});

/**
 * Story template listing
 */
storybase.builder.views.StoryTemplateView = Backbone.View.extend({
  tagName: 'li',

  className: 'template',

  templateSource: $('#story-template-template').html(),

  events: {
    "click a": "select"
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
  },

  render: function() {
    this.$el.html(this.template(this.model.toJSON()));
    return this;
  },

  /**
   * Event handler for clicking a template's link
   */
  select: function(e) {
    this.dispatcher.trigger("select:template", this.model);
    e.preventDefault();
  },

});

storybase.builder.views.BuilderView = Backbone.View.extend({
  tagName: 'div',

  className: 'builder',

  templateSource: $('#builder-template').html(),

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.dispatcher.on("select:template", this.setStoryTemplate, this);
    this.dispatcher.on("ready:templateSections", this.initializeStory, this);
    this.dispatcher.on("save:story", this.save, this);

    _.bindAll(this, 'addSectionThumbnail', 'setTemplateStory', 'setTemplateSections');

    this.template = Handlebars.compile(this.templateSource);
  },

  addSectionThumbnail: function(section) {
    console.debug("Adding section thumbnail"); 
    var view = new storybase.builder.views.SectionThumbnailView({
      dispatcher: this.dispatcher,
      model: section 
    });
    this.$(".sections").append(view.render().el);
  },

  render: function() {
    this.$el.html(this.template());
    if (!_.isUndefined(this.model)) {
      this.model.sections.each(this.addSectionThumbnail);
    }
    return this;
  },

  /**
   * Generic error handler
   *
   * This is basically a stub that can later propogate error messages
   * up to the UI
   */
  error: function(msg) {
    // TODO: More robust error handling
    console.error(msg);
  },

  setStoryTemplate: function(template) {
    console.debug("Setting story template");
    var that = this;
    this.storyTemplate = template;
    this.storyTemplate.getStory({
      success: this.setTemplateStory,
      error: function(story, response) {
        that.error("Failed fetching template story");
      }
    });
  },

  setTemplateStory: function(story) {
    console.debug("Setting template story");
    var that = this;
    this.templateStory = story;
    this.templateStory.fetchSections({
      success: this.setTemplateSections, 
      error: function(sections, response) {
        that.error("Failed fetching template story sections");
      }
    });
  },

  setTemplateSections: function(sections) {
    console.debug("Setting template sections"); 
    this.templateSections = sections;
    console.debug(this.templateSections);
    this.dispatcher.trigger("ready:templateSections");
  },

  initializeStory: function() {
    console.debug("Initializing sections");
    var that = this;
    // Create the story instance
    this.model = new storybase.models.Story({
      title: ""
    });
    this.model.sections = new storybase.collections.Sections([], {
      story: this.model
    });
    this.templateSections.each(function(section) {
      var sectionCopy = new storybase.models.Section();
      sectionCopy.set("title", section.get("title"));
      that.model.sections.push(sectionCopy);
    });
    this.render();
  },

  save: function() {
    console.debug("Saving story");
    var that = this;
    this.model.save(null, {
      success: function(model, response) {
        that.model.saveSections();
      }
    });
  }
});

storybase.builder.views.SectionThumbnailView = Backbone.View.extend({
  tagName: 'li',

  className: 'section-thumbnail',

  templateSource: $('#section-thumbnail-template').html(),

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
  },

  render: function() {
    this.$el.html(this.template(this.model.toJSON()));
    return this;
  }
});
