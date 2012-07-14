Namespace('storybase.builder.views');

storybase.builder.views.mixins = {};

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
    this.activeStep = this.model ? 'build' : 'selectTemplate';

    this.navView = new storybase.builder.views.NavigationView({
      el: this.$('#builder-nav'),
      dispatcher: this.dispatcher
    });

    // Store subviews in an object keyed with values of this.activeStep
    var buildViewOptions = {
      dispatcher: this.dispatcher,
      layouts: this.options.layouts,
      assetTypes: this.options.assetTypes
    };
    if (this.model) {
      buildViewOptions.model = this.model;
    }
    this.subviews = {
      selectTemplate: new storybase.builder.views.SelectStoryTemplateView({
        dispatcher: this.dispatcher,
        collection: this.options.storyTemplates
      }),
      build: new storybase.builder.views.BuilderView(buildViewOptions)
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
    this.dispatcher.trigger('navigate', 'story');
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
    this.$el.height($(window).height());
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
    var that = this;

    this._thumbnailViews = [];

    this.dispatcher = this.options.dispatcher;
    this.dispatcher.on("select:template", this.setStoryTemplate, this);
    this.dispatcher.on("ready:templateSections", this.initializeStoryFromTemplate, this);
    this.dispatcher.on("ready:story", this.storyReady, this);
    this.dispatcher.on("save:story", this.save, this);
    this.dispatcher.on("select:thumbnail", this.showEditView, this);

    _.bindAll(this, 'addSectionThumbnail', 'setTemplateStory', 'setTemplateSections');

    this.template = Handlebars.compile(this.templateSource);

    if (this.model) {
      this.model.fetchSections({
        success: function(sections) {
          that.dispatcher.trigger("ready:story");
        }
      });
    }
  },

  addSectionThumbnail: function(section) {
    console.debug("Adding section thumbnail");
    var view = new storybase.builder.views.SectionThumbnailView({
      dispatcher: this.dispatcher,
      model: section,
      editView: new storybase.builder.views.SectionEditView({
        dispatcher: this.dispatcher,
        model: section,
        story: this.model,
        assetTypes: this.options.assetTypes,
        layouts: this.options.layouts,
      })
    });
    this._thumbnailViews.splice(this._thumbnailViews.length - 1, 0, view);
  },

  addStoryInfoThumbnail: function() {
    var view = new storybase.builder.views.PseudoSectionThumbnailView({
      dispatcher: this.dispatcher,
      title: "Story Information",
      editView: new storybase.builder.views.StoryInfoEditView({
        dispatcher: this.dispatcher,
        model: this.model
      })
    });
    this._thumbnailViews.push(view);
  },

  addCallToActionThumbnail: function() {
    var view = new storybase.builder.views.PseudoSectionThumbnailView({
      dispatcher: this.dispatcher,
      title: "Call to Action",
      editView: new storybase.builder.views.CallToActionEditView({
        dispatcher: this.dispatcher,
        model: this.model
      })
    });
    this._thumbnailViews.push(view);
  },

  /**
   * Event handler for when the story model is ready.
   *
   * The story will either be ready when it has been cloned from the
   * template or when it has been fetched from the server.
   */
  storyReady: function() {
      this.addStoryInfoThumbnail();
      this.addCallToActionThumbnail();
      this.model.sections.each(this.addSectionThumbnail);
      this.render();
  },

  render: function() {
    var that = this;
    this.$el.html(this.template());
    if (this._thumbnailViews.length) {
      _.each(this._thumbnailViews, function(view) {
        that.$(".sections").append(view.render().el);
        that.$el.prepend(view.editView.render().el);
      });
      this.dispatcher.trigger("select:thumbnail", this._thumbnailViews[0]);
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
    this.dispatcher.trigger("ready:templateSections");
  },

  initializeStoryFromTemplate: function() {
    console.debug("Initializing sections");
    var that = this;
    // Create the story instance
    this.model = new storybase.models.Story({
      title: ""
    });
    this.templateSections.each(function(section) {
      var sectionCopy = new storybase.models.Section();
      sectionCopy.set("title", section.get("title"));
      sectionCopy.set("layout", section.get("layout"));
      sectionCopy.set("layout_template", section.get("layout_template"));
      that.model.sections.push(sectionCopy);
    });
    this.dispatcher.trigger("ready:story");
  },

  save: function() {
    console.debug("Saving story");
    var that = this;
    this.model.save(null, {
      success: function(model, response) {
        that.dispatcher.trigger('navigate', '/story/' + model.id + '/');
        model.saveSections();
      }
    });
  },

  showEditView: function(thumbnailView) {
    this.$('.edit-section').hide();
    thumbnailView.editView.render().$el.show();
  }
});

storybase.builder.views.mixins.ThumbnailHighlightMixin = {
  highlightClass: 'selected',

  /**
   * Highlight the thumbnail
   *
   * This method should be hooked up to a "select:thumbnail" event
   */
  highlight: function(view) {
    if (view == this) {
      this.$el.addClass(this.highlightClass);
    }
    else {
      this.$el.removeClass(this.highlightClass);
    }
  }
};

storybase.builder.views.SectionThumbnailView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.mixins.ThumbnailHighlightMixin, {
    tagName: 'li',

    className: 'section-thumbnail',

    templateSource: $('#section-thumbnail-template').html(),

    events: {
      "click": "select"
    },

    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      this.template = Handlebars.compile(this.templateSource);
      this.editView = this.options.editView;

      this.dispatcher.on("select:thumbnail", this.highlight, this);
      this.model.on("change", this.render, this);
    },

    render: function() {
      this.$el.html(this.template(this.model.toJSON()));
      return this;
    },

    select: function() {
      console.debug("Selecting section with id " + this.model.id);
      this.dispatcher.trigger("select:thumbnail", this);
    }
}));

storybase.builder.views.PseudoSectionThumbnailView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.mixins.ThumbnailHighlightMixin, {
    tagName: 'li',

    className: 'section-thumbnail pseudo',

    templateSource: $('#section-thumbnail-template').html(),

    events: {
      "click": "select"
    },

    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      this.template = Handlebars.compile(this.templateSource);
      this.editView = this.options.editView;

      this.title = this.options.title;

      this.dispatcher.on("select:thumbnail", this.highlight, this);
    },

    render: function() {
      var context = {
        title: this.title 
      };
      this.$el.html(this.template(context));
      return this;
    },

    select: function() {
      this.dispatcher.trigger("select:thumbnail", this);
    }
}));

/**
 * View for editing story metadata
 */
storybase.builder.views.StoryInfoEditView = Backbone.View.extend({
  tagName: 'div',

  className: 'edit-story-info edit-section',

  templateSource: $('#story-info-edit-template').html(),

  events: {
    "change input": 'change',
    "change textarea": 'change'
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
  },

  render: function() {
    this.$el.html(this.template(this.model.toJSON()));
    return this;
  },

  change: function(e) {
    var name = $(e.target).attr("name");
    var value = $(e.target).val();
    if (_.has(this.model.attributes, name)) {
      this.model.set(name, value);
      if (this.model.isNew()) {
        this.dispatcher.trigger("save:story");
      }
      else {
        this.model.save();
      }
      console.debug("Updated " + name + " to " + value);
    }
  }
});

/**
 * View for editing story metadata
 */
storybase.builder.views.CallToActionEditView = Backbone.View.extend({
  tagName: 'div',

  className: 'edit-call-to-action edit-section',

  templateSource: $('#story-call-to-action-edit-template').html(),

  events: {
    "change input": 'change'
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
  },

  render: function() {
    this.$el.html(this.template(this.model.toJSON()));
    return this;
  },

  change: function(e) {
    var name = $(e.target).attr("name");
    var value = $(e.target).val();
    if (_.has(this.model.attributes, name)) {
      this.model.set(name, value);
      if (this.model.isNew()) {
        this.dispatcher.trigger("save:story");
      }
      else {
        this.model.save();
      }
      console.debug("Updated " + name + " to " + value);
    }
  }
});

/**
 * View for editing a section
 */
storybase.builder.views.SectionEditView = Backbone.View.extend({
  tagName: 'div',

  className: 'edit-section',

  templateSource: $('#section-edit-template').html(),

  events: {
    "change input": 'change',
    "change select.layout": 'change'
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.story = this.options.story;
    this.layouts = this.options.layouts;
    this.template = Handlebars.compile(this.templateSource);
  },

  /**
   * Get a list of available section layouts in a format that can be
   * rendered in a template.
   */
  getLayoutContext: function() {
    var that = this;
    return _.map(this.layouts, function(layout) {
      return {
        name: layout.name,
        layout_id: layout.layout_id,
        selected: that.model.get('layout') == layout.layout_id
      };
    });
  },

  render: function() {
    var that = this;
    var context = this.model.toJSON();
    context.layouts = this.getLayoutContext();
    this.$el.html(this.template(context));
    this.$('.storybase-container-placeholder').each(function(index, el) {
      console.debug($(el).attr('id'));
      var sectionAssetView = new storybase.builder.views.SectionAssetEditView({
        el: el,
        dispatcher: that.dispatcher,
        assetTypes: that.options.assetTypes
      });
      sectionAssetView.render();
    });
    return this;
  },

  /**
   * Event handler for when form elements are changed
   */
  change: function(e) {
    console.debug("Change event!");
    var name = $(e.target).attr("name");
    var value = $(e.target).val();
    if (_.has(this.model.attributes, name)) {
      this.model.set(name, value);
      if (this.story.isNew()) {
        this.dispatcher.trigger("save:story");
      }
      else {
        this.model.save();
      }
      console.debug("Updated " + name + " to " + value);
    }
  },
});

storybase.builder.views.SectionAssetEditView = Backbone.View.extend({
  tagName: 'div',

  className: 'edit-section-asset',

  templateSource: function() {
    if (!_.isUndefined(this.model)) {
      return $('#section-asset-display-template').html();
    }
    else if (!_.isUndefined(this.type)) {
      return $('#section-asset-edit-template').html();
    }
    else {
      return $('#section-asset-select-type-template').html();
    }
  },

  events: {
    "click .asset-type": "selectType", 
    'click input[type="reset"]': "cancel",
    'click input[type="submit"]': "save"
  },

  showUrl: {
    'image': true,
    'audio': true,
    'video': true,
    'map': true,
    'table': true,
  },

  showFile: {
    'image': true,
    'map': true
  },

  showBody: {
    'text': true,
    'quotation': true
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.assetTypes = this.options.assetTypes;
  },

  render: function() {
    this.template = Handlebars.compile(this.templateSource());
    var context = {
      assetTypes: this.assetTypes
    };
    if (!_.isUndefined(this.type)) {
      context.showUrl = this.type in this.showUrl,
      context.showFile = this.type in this.showFile, 
      context.showBody = this.type in this.showBody 
    }
    if (!_.isUndefined(this.model)) {
      context.model = this.model.toJSON()
    }
    this.$el.html(this.template(context));
    return this;
  },

  /**
   * Event handler for selecting asset type
   */
  selectType: function(e) {
    e.preventDefault(); 
    this.type = $(e.target).data('asset-type');
    this.render();
  },

  /**
   * Event handler for canceling form interaction
   */
  cancel: function(e) {
    e.preventDefault();
    if (_.isUndefined(this.model)) {
      // No asset has been saved for this view, just forget the type
      delete this.type;
    }
    this.render();
  },

  /**
   * Event handler for saving form
   */
  save: function(e) {
    var that = this;
    console.debug("Creating asset");
    e.preventDefault();
    if (_.isUndefined(this.model)) {
      this.model = new storybase.models.Asset({
        type: this.type
      });
    }
    this.model.save(null, {
      success: function(model) {
        that.render();
      }
    });
  }
});
