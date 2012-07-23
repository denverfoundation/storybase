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
    var commonOptions = {
      dispatcher: this.dispatcher,
    };

    // Initialize the view for the workflow step indicator
    this.workflowStepView = new storybase.builder.views.WorkflowStepView(
      commonOptions
    );
    // TODO: Change the selector as the template changes
    this.$('header').first().children().first().append(this.workflowStepView.el);
    // Initialize a view for the tools menu
    this.toolsView = new storybase.builder.views.ToolsView(commonOptions);
    
    // TODO: Change the selector as the template changes
    this.$('header').first().children().first().append(this.toolsView.el);
    // Initialize view for moving back and forth through the workflow steps
    this.workflowNavView = new storybase.builder.views.WorkflowNavView(
      commonOptions
    );
    this.helpView = new storybase.builder.views.HelpView(commonOptions);

    // Store subviews in an object keyed with values of this.activeStep
    if (this.model) {
      commonOptions.model = this.model;
    }
    var buildViewOptions = _.extend(commonOptions, {
      assetTypes: this.options.assetTypes,
      layouts: this.options.layouts,
      help: this.options.help
    });
    this.subviews = {
      selectTemplate: new storybase.builder.views.SelectStoryTemplateView({
        dispatcher: this.dispatcher,
        collection: this.options.storyTemplates
      }),
      build: new storybase.builder.views.BuilderView(buildViewOptions),
      data: new storybase.builder.views.DataView(commonOptions),
      review: new storybase.builder.views.ReviewView(commonOptions),
      share: new storybase.builder.views.ShareView(commonOptions)
    };
    // The currently active step of the story building process
    this.activeStep = this.model ? 'build' : 'selectTemplate';

    // Bind callbacks for custom events
    this.dispatcher.on("select:template", this.setTemplate, this);
    this.dispatcher.on("select:workflowstep", this.updateStep, this); 
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
    console.debug('Rendering main view');
    var activeView = this.getActiveView();
    this.$el.height($(window).height());
    this.$('#app').html(activeView.render().$el);
    this.$('#app').append(this.workflowNavView.render().el);
    this.workflowStepView.render();
    this.toolsView.render();
    return this;
  }
});

storybase.builder.views.HelpView = Backbone.View.extend({
  tagName: 'div',

  className: 'help',

  templateSource: $('#help-template').html(),

  events: {
    'change .auto-show-help': 'setAutoShow'
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.help = null;
    this.template = Handlebars.compile(this.templateSource);
    // Always show help when switching to a new section
    this.autoShow = true;

    this.dispatcher.on('do:show:help', this.show, this);
  },

  setAutoShow: function(evt) {
    this.autoShow = $(evt.target).prop('checked'); 
  },

  /**
   * Show the help text via a modal window.
   *
   * @param boolean force Force showing the help in a modal, overriding
   *     the value of this.autoShow.
   * @help object help Updated help information.  The object should have
   *     a body property and optionally a title property.
   *
   * @returns object This view.
   */
  show: function(force, help) {
    var show = this.autoShow || force;
    if (!_.isUndefined(help)) {
      // A new help object was sent with the signal, update
      // our internal value
      this.help = help;
    }
    if (this.help) {
      this.render();
      if (show) {
        this.delegateEvents();
        this.$el.modal();
      }
    }
    return this;
  },

  render: function() {
    var context = _.extend(this.help, {
      'autoShow': this.autoShow
    });
    this.$el.html(this.template(this.help));
    return this;
  }
});

/**
 * Base class for menu-like views
 */
storybase.builder.views.MenuView = Backbone.View.extend({
  items: [],

  itemTemplateSource: $('#menu-item-template').html(),

  getItemTemplate: function() {
    if (_.isUndefined(this.itemTemplate)) {
      this.itemTemplate = Handlebars.compile(this.itemTemplateSource);
    }
    return this.itemTemplate; 
  },

  events: function() {
    var events = {};
    _.each(this.items, function(item) {
      if (item.callback) {
        events["click ." + item.id] = item.callback;
      }
    });
    return events;
  },

  getItem: function(id) {
    return _.filter(this.items, function(item) {
      return item.id === id;
    })[0];
  },

  setVisibility: function(id, visible) {
    var item = this.getItem(id);
    item.visible = visible;
  },

  getVisibleItems: function() {
    return _.filter(this.items, function(item) {
      return item.visible == true;
    });
  }
});

/**
 * Shows current step of workflow 
 */
storybase.builder.views.WorkflowStepView = storybase.builder.views.MenuView.extend({
  tagName: 'ul',

  className: 'workflow nav',

  itemTemplateSource: $('#workflow-item-template').html(),

  items: [
    {
      id: 'build',
      title: 'Build',
      callback: 'selectStage',
      visible: true,
      path: ''
    },
    {
      id: 'data',
      title: 'Add Data',
      callback: 'selectStage',
      visible: false,
      path: 'data/'
    },
    {
      id: 'review',
      title: 'Review',
      callback: 'selectStage',
      visible: false,
      path: 'review/'
    },
    {
      id: 'share',
      title: 'Share',
      callback: 'selectStage',
      visible: false,
      path: 'share/legal/'
    }
  ],

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
    this.storyId = null;

    this.dispatcher.on('ready:story', this.showWorkflowItems, this);
    this.dispatcher.on('save:story', this.showWorkflowItems, this);
    this.dispatcher.on('ready:story', this.setStoryId, this);
    this.dispatcher.on('save:story', this.setStoryId, this);
    this.dispatcher.on('select:workflowstep', this.highlightActive, this);
  },


  render: function() {
    var that = this;
    var template = this.getItemTemplate();
    var context = {
      storyId: this.storyId
    };
    this.$el.empty();
    _.each(this.getVisibleItems(), function(item) {
      that.$el.append(template(_.extend(item, context)));
    });
    return this;
  },


  setStoryId: function(story) {
    if (!story.isNew()) {
      this.storyId = story.id; 
    }
  },

  /**
   * Show the worfklow items that require a story.
   */
  showWorkflowItems: function(story) {
    if (!story.isNew()) {
      this.setVisibility('data', true);
      this.setVisibility('review', true);
      this.setVisibility('share', true);
      this.render();
    }
    return this;
  },

  selectStage: function(evt) {
    evt.preventDefault();
    var route = $(evt.target).attr("href");
    this.dispatcher.trigger('navigate', route, 
      {trigger: true, replace: true});
  },

  highlightActive: function(step) {
    _.each(this.items, function(item) {
      if (item.id === step) {
        item.active = true;
      }
      else {
        item.active = false;
      }
    });
    return this.render();
  }
});

storybase.builder.views.ToolsView = storybase.builder.views.MenuView.extend({
  tagName: 'ul',

  className: 'tools nav',

  items: [
    {
      id: 'help',
      title: 'Help',
      callback: 'toggleHelp', 
      href: '#',
      visible: true 
    },
    {
      id: 'assets',
      title: 'Assets',
      callback: 'toggleAssetList',
      href: '#',
      visible: false
    },
    {
      id: 'preview',
      title: 'Preview',
      callback: null,
      href: '#',
      visible: false
    },
    {
      id: 'exit',
      title: 'Exit',
      callback: null,
      href: '/',
      visible: true 
    },
  ],

  initialize: function() {
    this.dispatcher = this.options.dispatcher;

    this.dispatcher.on('has:assetlist', this.toggleAssetsItem, this);
    this.dispatcher.on('ready:story', this.setStoryId, this);
    this.dispatcher.on('save:story', this.setStoryId, this);
  },

  render: function() {
    var that = this;
    var template = this.getItemTemplate();
    this.$el.empty();
    _.each(this.getVisibleItems(), function(item) {
      that.$el.append(template(item));
    });
    return this;
  },

  toggleAssetsItem: function(visible) {
    this.setVisibility('assets', visible);
    this.render();
  },

  toggleAssetList: function(evt) {
    evt.preventDefault();
    this.dispatcher.trigger("toggle:assetlist");
  },

  toggleHelp: function(evt) {
    evt.preventDefault();
    this.dispatcher.trigger('do:show:help', true);
  },
  
  setStoryId: function(story) {
    if (!story.isNew() && _.isUndefined(this.storyId)) {
      var item = this.getItem('preview');
      this.storyId = story.id; 
      item.href = '/stories/' + this.storyId + '/viewer/';
      item.visible = true;
      this.render();
    }
  }
});

/**
 * A pair of links that lets the user move forward and back through the
 * different workflow steps.
 */
storybase.builder.views.WorkflowNavView = storybase.builder.views.MenuView.extend({
  tagName: 'div',

  className: 'workflow-nav',

  itemTemplateSource: $('#workflow-nav-item-template').html(),

  items: [
    {
      id: 'build',
      backTitle: 'Continue Writing Story',
      callback: 'selectStage',
      path: ''
    },
    {
      id: 'data',
      fwdTitle: 'Add Data',
      backTitle: 'Back to "Add Data"',
      callback: 'selectStage',
      path: 'data/'
    },
    {
      id: 'review',
      backTitle: 'Back to Review',
      fwdTitle: 'Review',
      callback: 'selectStage',
      path: 'review/'
    },
    {
      id: 'share-legal',
      backTitle: 'Back to Legal Agreements',
      fwdTitle: 'Share My Story',
      callback: 'selectStage',
      path: 'share/legal/'
    },
    {
      id: 'share-tagging',
      backTitle: 'Back to Tagging',
      fwdTitle: 'Continue',
      callback: 'selectStage',
      path: 'share/tagging/'
    },
    {
      id: 'share-publish',
      fwdTitle: 'Continue',
      callback: 'selectStage',
      path: 'share/publish/'
    },
    {
      id: 'new',
      fwdTitle: 'Tell Another Story',
      callback: null, 
      href: '/build'
    }
  ],

  visibility: {
    'build': {
      back: null,
      forward: 'data'
    },
    'data': {
      back: 'build',
      forward: 'review'
    },
    'review': {
      back: 'data',
      forward: 'share-legal'
    },
    'share-legal': {
      back: 'review',
      forward: 'share-tagging'
    },
    'share-tagging': {
      back: 'share-legal',
      forward: 'share-publish'
    },
    'share-publish': {
      back: 'share-tagging',
      forward: 'new'
    }
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.forward = this.getItem('data');
    this.back = null;

    this.dispatcher.on('ready:story', this.setStoryId, this);
    this.dispatcher.on('save:story', this.setStoryId, this);
    this.dispatcher.on('select:workflowstep', this.selectVisible, this);
  },

  render: function() {
    console.info('Rendering navigation view');
    var that = this;
    var template = this.getItemTemplate();
    this.$el.empty();
    if (this.storyId) {
      if (this.back) {
        this.$el.append(template({
          id: this.back.id,
          title: this.back.backTitle,
          href: this.getHref(this.back) 
        }));
      }
      if (this.forward) {
        this.$el.append(template({
          id: this.forward.id,
          title: this.forward.fwdTitle,
          href: this.getHref(this.forward)
        }));
      }
    }
    this.delegateEvents();
    return this;
  },

  selectVisible: function(step, subStep) {
    console.debug('Entering selectVisible');
    var key = _.isUndefined(subStep) ? step : step + '-' + subStep;
    this.forward = this.visibility[key].forward ? this.getItem(this.visibility[key].forward) : null;
    this.back = this.visibility[key].back ? this.getItem(this.visibility[key].back) : null;
    this.render();
    return this;
  },

  selectStage: function(evt) {
    evt.preventDefault();
    var route = $(evt.target).attr("href");
    this.dispatcher.trigger('navigate', route, 
      {trigger: true, replace: true});
  },

  setStoryId: function(story) {
    if (!story.isNew() && _.isUndefined(this.storyId)) {
      this.storyId = story.id; 
      this.render();
    }
  },

  getHref: function(item) {
    if (!_.isUndefined(item.href)) {
      return item.href;
    }
    if (!_.isUndefined(item.path)) {
      return this.storyId + '/' + item.path;
    }

    return '#';
  },
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
    console.info('initializing form');
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

storybase.builder.views.AlertView = Backbone.View.extend({
  tagName: 'div',

  className: 'alert',

  initialize: function() {
    this.level = this.options.level;
    this.message = this.options.message;
  },

  render: function() {
    this.$el.addClass('alert-' + this.level);
    this.$el.html(this.message);
    return this;
  }
});

storybase.builder.views.BuilderView = Backbone.View.extend({
  tagName: 'div',

  className: 'builder',

  templateSource: $('#builder-template').html(),

  initialize: function() {
    var that = this;

    this.dispatcher = this.options.dispatcher;
    this.help = this.options.help;
    
    if (_.isUndefined(this.model)) {
      // Create a new story model instance
      this.model = new storybase.models.Story({
        title: ""
      });
    }
    else {
      // The view was constructed with a model instance,
      // which means it was a previously created story
      // Tell other views about it
      this.dispatcher.trigger('ready:story', this.model);
    }

    this._thumbnailViews = [];
    this.unusedAssetView = new storybase.builder.views.UnusedAssetView({
      dispatcher: this.dispatcher,
      assets: this.model.unusedAssets
    });
    this.lastSavedView = new storybase.builder.views.LastSavedView({
      dispatcher: this.dispatcher,
      lastSaved: this.model.get('last_edited')
    });

    this.model.on("sync", this.triggerSaved, this);
    this.model.on("sync", this.showSaved, this);
    this.model.unusedAssets.on("sync reset add", this.hasAssetList, this);

    this.dispatcher.on("select:template", this.setStoryTemplate, this);
    this.dispatcher.on("ready:templateSections", this.initializeStoryFromTemplate, this);
    this.dispatcher.on("ready:story", this.storyReady, this);
    this.dispatcher.on("do:save:story", this.save, this);
    this.dispatcher.on("select:thumbnail", this.showEditView, this);
    this.dispatcher.on("toggle:assetlist", this.toggleAssetList, this);
    this.dispatcher.on("add:sectionasset", this.showSaved, this);
    this.dispatcher.on("save:section", this.showSaved, this);
    this.dispatcher.on("error", this.error, this);
    this.dispatcher.on("alert", this.showAlert, this);

    _.bindAll(this, 'addSectionThumbnail', 'setTemplateStory', 'setTemplateSections');

    this.template = Handlebars.compile(this.templateSource);

    this.model.sections.on("reset", this.storyReady, this);
    if (!this.model.isNew()) {
      this.model.sections.fetch();
      this.model.unusedAssets.fetch();
    }
  },

  addSectionThumbnail: function(section) {
    console.info("Adding section thumbnail");
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
        help: this.help.where({slug: 'story-information'})[0],
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
        help: this.help.where({slug: 'call-to-action'})[0],
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
    console.info('Rendering builder view');
    var that = this;
    this.$el.html(this.template());
    this.$el.prepend(this.unusedAssetView.render().$el.hide());
    this.$el.prepend(this.lastSavedView.render().el);
    if (this._thumbnailViews.length) {
      _.each(this._thumbnailViews, function(view) {
        that.$(".sections").append(view.render().el);
        that.$('.sections').before(view.editView.render().el);
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
    console.error(msg);
    this.showAlert('error', msg);
  },

  showAlert: function(level, msg) {
    var view = new storybase.builder.views.AlertView({
      level: level,
      message: msg
    });
    this.$('.alerts').prepend(view.render().el);
    view.$el.fadeOut(5000, function() {
      $(this).remove();
    });
  },

  showSaved: function() {
    this.showAlert('success', "The story has been saved");
  },

  triggerSaved: function() {
    this.dispatcher.trigger('save:story', this.model);
  },

  setStoryTemplate: function(template) {
    console.info("Setting story template");
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
    console.info("Setting template story");
    var that = this;
    this.templateStory = story;
    this.templateStory.sections.on("reset", this.setTemplateSections, this);
    this.templateStory.sections.fetch();
  },

  setTemplateSections: function(sections) {
    console.info("Setting template sections"); 
    this.templateSections = sections;
    this.dispatcher.trigger("ready:templateSections");
  },

  initializeStoryFromTemplate: function() {
    console.info("Initializing sections");
    var that = this;
    this.model.set('structure_type',
                   this.templateStory.get('structure_type'));
    this.templateSections.each(function(section) {
      var sectionCopy = new storybase.models.Section();
      sectionCopy.set("title", section.get("title"));
      sectionCopy.set("layout", section.get("layout"));
      sectionCopy.set("root", section.get("root"));
      sectionCopy.set("layout_template", section.get("layout_template"));
      sectionCopy.set("help", section.get("help"));
      that.model.sections.push(sectionCopy);
    });
    this.dispatcher.trigger("ready:story", this.model);
  },

  save: function() {
    console.info("Saving story");
    var that = this;
    this.model.save(null, {
      success: function(model, response) {
        that.dispatcher.trigger('save:story', model);
        that.dispatcher.trigger('navigate', model.id + '/');
        model.saveSections();
      }
    });
  },

  showEditView: function(thumbnailView) {
    this.$('.edit-section').hide();
    //thumbnailView.editView.$el.show();
    thumbnailView.editView.show();
  },

  toggleAssetList: function() {
    this.unusedAssetView.$el.toggle(); 
  },

  hasAssetList: function() {
    var hasAssets = false;
    if (this.model.unusedAssets.length) {
      hasAssets = true; 
    }
    this.dispatcher.trigger('has:assetlist', hasAssets);
  }
});

storybase.builder.views.LastSavedView = Backbone.View.extend({
  tagName: 'div',

  className: 'last-saved',

  initialize: function() {
    this.lastSaved = _.isUndefined(this.options.lastSaved) ? undefined : (_.isDate(this.options.lastSaved) ? this.options.lastSaved : new Date(this.options.lastSaved));
    this.dispatcher = this.options.dispatcher;

    this.dispatcher.on('save:section', this.updateLastSaved, this);
    this.dispatcher.on('save:story', this.updateLastSaved, this);
  },

  updateLastSaved: function() {
    this.lastSaved = new Date(); 
    this.render();
  },

  /**
   * Ensure that an hour or minute value is 2 digits
   *
   * This is necesary because Date.getHours and Date.getDate return 
   * integer values starting from 0
   *
   */
  twoDigit: function(val) {
    var newVal = val + "";
    if (newVal.length == 1) {
      newVal = "0" + newVal;
    }
    return newVal;
  },

  formatDate: function(date) {
    var year = this.lastSaved.getFullYear();
    var month = this.lastSaved.getMonth() + 1;
    var day = this.lastSaved.getDate();
    var hour = this.lastSaved.getHours();
    var minute = this.lastSaved.getMinutes();

    return month + "/" + day + "/" + year + " " + this.twoDigit(hour) +
           ":" + this.twoDigit(minute);
  },

  render: function() {
    if (this.lastSaved) {
      this.$el.html('Last Saved: ' + this.formatDate(this.lastSaved));
    }
    return this;
  }
});

/** 
 * A list of assets associated with the story but not used in any section.
 */
storybase.builder.views.UnusedAssetView = Backbone.View.extend({
  tagName: 'div',

  className: 'unused-assets',

  templateSource: $('#unused-assets-template').html(),

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
    this.assets = this.options.assets;

    // When the assets are synced with the server, re-render this view
    this.assets.on("add reset sync", this.render, this);
    // When an asset is removed from a section, add it to this view
    this.dispatcher.on("remove:sectionasset", this.addAsset, this);
  },

  render: function() {
    var context = {
      assets: this.assets.toJSON()
    };
    this.$el.html(this.template(context));
    return this;
  },

  /**
   * Event callback for when assets are removed from a section
   */
  addAsset: function(asset) {
    this.assets.push(asset);
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
      this.delegateEvents();
      return this;
    },

    select: function() {
      console.info("Selecting section with id " + this.model.id);
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
      this.delegateEvents();
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
    this.help = this.options.help;
    this.template = Handlebars.compile(this.templateSource);
  },

  render: function() {
    this.$el.html(this.template(this.model.toJSON()));
    return this;
  },

  show: function() {
    this.$el.show();
    this.dispatcher.trigger('do:show:help', false, this.help.toJSON()); 
    return this;
  },

  change: function(e) {
    var name = $(e.target).attr("name");
    var value = $(e.target).val();
    if (_.has(this.model.attributes, name)) {
      this.model.set(name, value);
      if (this.model.isNew()) {
        this.dispatcher.trigger("do:save:story");
      }
      else {
        this.model.save();
      }
      console.info("Updated " + name + " to " + value);
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
    'change textarea[name="call_to_action"]': 'change'
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.help = this.options.help;
    this.template = Handlebars.compile(this.templateSource);
  },

  render: function() {
    this.$el.html(this.template(this.model.toJSON()));
    return this;
  },

  show: function() {
    this.$el.show();
    this.dispatcher.trigger('do:show:help', false, this.help.toJSON()); 
    return this;
  },

  change: function(e) {
    var name = $(e.target).attr("name");
    var value = $(e.target).val();
    if (_.has(this.model.attributes, name)) {
      this.model.set(name, value);
      if (this.model.isNew()) {
        this.dispatcher.trigger("do:save:story");
      }
      else {
        this.model.save();
      }
      console.info("Updated " + name + " to " + value);
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
    this.templateSource = this.options.templateSource || this.templateSource;
    this.template = Handlebars.compile(this.templateSource);
    this.assets = this.options.assets || new storybase.collections.SectionAssets();
    this._unsavedAssets = [];
    this._doConditionalRender = false;

    _.bindAll(this, 'renderAssetViews');
    this.dispatcher.on('do:add:sectionasset', this.addAsset, this);
    this.dispatcher.on('do:remove:sectionasset', this.removeAsset, this);
    this.model.on("change:layout", this.changeLayout, this);
    this.model.on("sync", this.saveSectionAssets, this);
    this.model.on("sync", this.conditionalRender, this);
    this.model.on("sync", this.triggerSaved, this);
    this.assets.on("reset sync", this.renderAssetViews, this);
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

  renderAssetViews: function() {
    var that = this;
    this.$('.storybase-container-placeholder').each(function(index, el) {
      var options = {
        el: el,
        container: $(el).attr('id'),
        dispatcher: that.dispatcher,
        assetTypes: that.options.assetTypes
      };
      if (that.assets.length) {
        // If there are assets, bind them to the view with the appropriate
        // container
        options.model = that.assets.where({container: $(el).attr('id')})[0];
      }
      var sectionAssetView = new storybase.builder.views.SectionAssetEditView(options);
      sectionAssetView.render();
    });
  },

  render: function() {
    var context = this.model.toJSON();
    context.layouts = this.getLayoutContext();
    this.$el.html(this.template(context));
    if (this.model.isNew()) {
      this.renderAssetViews();
    }
    else {
      this.assets.url = this.model.url() + 'assets/';
      this.assets.fetch();
    }
    return this;
  },

  show: function() {
    this.$el.show();
    // TODO: Figure out how to show help
    // BOOKMARK
    this.dispatcher.trigger('do:show:help', false, 
                            this.model.get('help')); 
    return this;
  },

  setConditionalRender: function() {
    this._doConditionalRender = true;
  },

  conditionalRender: function() {
    if (this._doConditionalRender === true) {
      this.render();
    }
    this._doConditionalRender = false;
  },

  /**
   * Event handler for when form elements are changed
   */
  change: function(e) {
    console.info("Change event!");
    var name = $(e.target).attr("name");
    var value = $(e.target).val();
    if (_.has(this.model.attributes, name)) {
      this.model.set(name, value);
      if (this.story.isNew()) {
        this.dispatcher.trigger("do:save:story");
      }
      else {
        this.model.save();
      }
      console.info("Updated " + name + " to " + value);
    }
  },

  changeLayout: function(evt) {
    this.setConditionalRender();
    this.removeAssets();
  },

  /**
   * Disassociate all assets with this section. 
   */
  removeAssets: function() {
    var that = this;
    this.assets.each(function(asset) {
      that.removeAsset(asset);
    });
  },

  /**
   * Event handler for when assets are added to the section
   */
  addAsset: function(asset, container) {
    this.assets.add(asset);
    if (this.story.isNew()) {
      // We haven't saved the story or the section yet.
      // Defer the saving of the asset relation 
      this._unsavedAssets.push({
        asset: asset,
        container: container
      });
      // Trigger an event that will cause the story and section to be saved
      this.dispatcher.trigger("do:save:story");
    }
    else {
      this.saveSectionAsset(asset, container);
    }
  },

  /**
   * Event handler for when assets are removed from the section
   */
  removeAsset: function(asset) {
    var that = this;
    var sectionAsset = this.getSectionAsset(asset);
    sectionAsset.id = asset.id;
    sectionAsset.destroy({
      success: function(model, response) {
        that.dispatcher.trigger("remove:sectionasset", asset);
        that.dispatcher.trigger("alert", "info", "You removed an asset, but it's not gone forever. You can re-add it to a section from the asset list");
      },
      error: function(model, response) {
        that.dispatcher.trigger("error", "Error removing asset from section");
      }
    });
  },

  getSectionAsset: function(asset, container) {
    var SectionAsset = Backbone.Model.extend({
      urlRoot: this.model.url() + 'assets',
      url: function() {
        return Backbone.Model.prototype.url.call(this) + '/';
      }
    });
    var sectionAsset = new SectionAsset({
      asset: asset.url(),
      container: container
    });
    sectionAsset.on("sync", this.sectionAssetAdded, this);
    return sectionAsset;
  },

  saveSectionAsset: function(asset, container) {
    this.getSectionAsset(asset, container).save();
  },

  saveSectionAssets: function() {
    var that = this;
    _.each(this._unsavedAssets, function(sectionAsset) {
      that.saveSectionAsset(sectionAsset.asset, sectionAsset.container); 
    });
    this._unsavedAssets = [];
  },

  sectionAssetAdded: function() {
    this.dispatcher.trigger("add:sectionasset");
  },

  triggerSaved: function() {
    this.dispatcher.trigger('save:section', this.model);
  },

});

storybase.builder.views.SectionAssetEditView = Backbone.View.extend({
  tagName: 'div',

  className: 'edit-section-asset',

  templateSource: function() {
    var state = this.getState(); 
    if (state === 'display') {
      return $('#section-asset-display-template').html();
    }
    else if (state === 'edit') {
      return $('#section-asset-edit-template').html();
    }
    else {
      // state === 'select'
      return $('#section-asset-select-type-template').html();
    }
  },

  events: {
    "click .asset-type": "selectType", 
    "click .remove": "remove",
    "click .edit": "edit",
    'click input[type="reset"]': "cancel",
    'submit form': 'processForm'
  },

  initialize: function() {
    this.container = this.options.container;
    this.dispatcher = this.options.dispatcher;
    this.assetTypes = this.options.assetTypes;
    if (_.isUndefined(this.model)) {
      this.model = new storybase.models.Asset();
    }
    _.bindAll(this, 'initializeForm'); 
    this.model.on("change", this.initializeForm);
    this.initializeForm();
    this.setInitialState();
  },

  /**
   * Set the view's form property based on the current state of the model.
   */
  initializeForm: function() {
    console.info('Initializing form');
    this.form = new Backbone.Form({
      model: this.model
    });
    this.form.render();
  },

  render: function() {
    this.template = Handlebars.compile(this.templateSource());
    var context = {
      assetTypes: this.assetTypes
    };
    var state = this.getState();
    if (state === 'display') {
      context.model = this.model.toJSON()
    }
    this.$el.html(this.template(context));
    if (state === 'edit') {
      this.form.render().$el.append('<input type="reset" value="Cancel" />').append('<input type="submit" value="Save" />');
      this.$el.append(this.form.el);
    }
    return this;
  },

  setInitialState: function() {
    if (!this.model.isNew()) {
      this._state = 'display';
    }
    else if (!_.isUndefined(this.model.type)) {
      this._state = 'edit';
    }
    else {
      this._state = 'select';
    }
  },

  getState: function() {
    return this._state;
  },

  setState: function(state) {
    this._state = state;
    return this;
  },

  /**
   * Event handler for selecting asset type
   */
  selectType: function(e) {
    e.preventDefault(); 
    this.setType($(e.target).data('asset-type'));
  },

  setType: function(type) {
    this.model.set('type', type);
    this.initializeForm();
    this.setState('edit').render();
  },

  /**
   * Event handler for canceling form interaction
   */
  cancel: function(e) {
    e.preventDefault();
    if (this.model.isNew()) {
      this.setState('select');
    }
    else {
      this.setState('display');
    }
    this.render();
  },

  saveModel: function(attributes) {
    var that = this;
    // Save the model's original new state to decide
    // whether to send a signal later
    var isNew = this.model.isNew();
    this.model.save(attributes, {
      success: function(model) {
        // TODO: Decide if it's better to listen to the model's
        // "sync" event than to use this callback
        that.setState('display');
        that.render();
        if (isNew) {
          // Model was new before saving
          that.dispatcher.trigger("do:add:sectionasset", that.model, that.container);
        }
      },
      error: function(model) {
        that.dispatcher.trigger('error', 'error saving the asset');
      }
    });
  },

  /**
   * Event handler for submitting form
   */
  processForm: function(e) {
    e.preventDefault();
    console.info("Creating asset");
    var that = this;
    var errors = this.form.validate();
    if (!errors) {
      var data = this.form.getValue();
      if (data.image) {
        data.filename = data.image;
        this.form.fields.image.editor.getValueAsDataURL(function(dataURL) {
          data.image = dataURL;
          that.saveModel(data);
        });
      }
      else {
        this.saveModel(data);
      }
    }
    else {
      // Remove any previous error messages
      this.form.$('.bbf-model-errors').remove();
      if (!_.isUndefined(errors._others)) {
        that.form.$el.prepend('<ul class="bbf-model-errors">');
        _.each(errors._others, function(msg) {
          that.form.$('.bbf-model-errors').append('<li>' + msg + '</li>');
        });
      }
    }
  },

  edit: function(evt) {
    evt.preventDefault();
    this.setState('edit').render();
  },

  remove: function(evt) {
    evt.preventDefault();
    this.dispatcher.trigger('do:remove:sectionasset', this.model);
    this.model = new storybase.models.Asset();
    this.setState('select').render();
  }
});

storybase.builder.views.DataView = Backbone.View.extend({
  templateSource: $('#data-template').html(),

  events: {
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
  },

  render: function() {
    console.info('Rendering data view');
    var context = {};
    this.$el.html(this.template(context));
    return this;
  }
});

storybase.builder.views.ReviewView = Backbone.View.extend({
  templateSource: $('#review-template').html(),

  events: {
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
  },

  render: function() {
    console.info('Rendering review view');
    var context = {};
    this.$el.html(this.template(context));
    return this;
  }
});

storybase.builder.views.ShareView = Backbone.View.extend({
  templateSource: $('#share-template').html(),

  events: {
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
  },

  render: function() {
    console.info('Rendering share view');
    var context = {};
    this.$el.html(this.template(context));
    return this;
  }
});
