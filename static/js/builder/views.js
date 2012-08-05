Namespace('storybase.builder.views');

/**
 * @name save:section
 * @event
 * @param Section section Event triggered when a section has successfully
 *     been saved.
 * @param Boolean showAlert Should an alert be displayed by a callback 
 *     bound to this event.
 */

/**
 * @name save:story
 * @event
 * @param Story story Event triggered when a story has successfully
 *     been saved.
 * @param Boolean showAlert Should an alert be displayed by a callback 
 *     bound to this event.
 */

/**
 * Master view for the story builder
 *
 * Dispatches to sub-views.
 */
storybase.builder.views.AppView = Backbone.View.extend({
  initialize: function() {
    // Common options passed to sub-views
    var commonOptions = {};
    this.dispatcher = this.options.dispatcher;
    commonOptions.dispatcher = this.dispatcher;
    // The currently active step of the story building process
    // This will get set by an event callback 
    this.activeStep = null; 

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
      selecttemplate: new storybase.builder.views.SelectStoryTemplateView({
        dispatcher: this.dispatcher,
        collection: this.options.storyTemplates
      }),
      build: new storybase.builder.views.BuilderView(buildViewOptions),
      data: new storybase.builder.views.DataView(commonOptions),
      review: new storybase.builder.views.ReviewView(commonOptions),
      share: new storybase.builder.views.ShareView(commonOptions)
    };

    // Bind callbacks for custom events
    this.dispatcher.on("select:template", this.setTemplate, this);
    this.dispatcher.on("select:workflowstep", this.updateStep, this); 
    this.dispatcher.on("error", this.error, this);
    this.dispatcher.on("alert", this.showAlert, this);
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
    console.debug('Updating active view to ' + step);
    this.activeStep = step;
    this.render();
  },

  /**
   * Get the sub-view for the currently active step
   */
  getActiveView: function() {
    console.debug('Getting active view for step ' + this.activeStep);
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
    this.$('.alerts').empty();
    this.$('.alerts').prepend(view.render().el);
    view.$el.fadeOut(5000, function() {
      $(this).remove();
    });
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
      callback: 'selectStep',
      visible: true,
      path: ''
    },
    {
      id: 'data',
      title: 'Add Data',
      callback: 'selectStep',
      visible: false,
      path: 'data/'
    },
    {
      id: 'review',
      title: 'Review',
      callback: 'selectStep',
      visible: false,
      path: 'review/'
    },
    {
      id: 'share',
      title: 'Share',
      callback: 'selectStep',
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

  selectStep: function(evt) {
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
      callback: 'selectStep',
      path: ''
    },
    {
      id: 'data',
      fwdTitle: 'Add Data',
      backTitle: 'Back to "Add Data"',
      callback: 'selectStep',
      path: 'data/'
    },
    {
      id: 'review',
      backTitle: 'Back to Review',
      fwdTitle: 'Review',
      callback: 'selectStep',
      path: 'review/'
    },
    {
      id: 'share-legal',
      backTitle: 'Back to Legal Agreements',
      fwdTitle: 'Share My Story',
      callback: 'selectStep',
      path: 'share/legal/'
    },
    {
      id: 'share-tagging',
      backTitle: 'Back to Tagging',
      fwdTitle: 'Continue',
      callback: 'selectStep',
      path: 'share/tagging/'
    },
    {
      id: 'share-publish',
      fwdTitle: 'Continue',
      callback: 'selectStep',
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
    'selecttemplate': {
      back: null,
      forward: null
    },

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
    console.debug('Selecting step ' + step);
    if (!_.isUndefined(subStep)) {
      console.debug('Selecting sub-step ' + subStep);
    }
    var key = _.isUndefined(subStep) ? step : step + '-' + subStep;
    this.forward = this.visibility[key].forward ? this.getItem(this.visibility[key].forward) : null;
    this.back = this.visibility[key].back ? this.getItem(this.visibility[key].back) : null;
    this.render();
    return this;
  },

  selectStep: function(evt) {
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

    this.sectionListView = new storybase.builder.views.SectionListView({
      dispatcher: this.dispatcher,
      model: this.model
    });
    this.unusedAssetView = new storybase.builder.views.UnusedAssetView({
      dispatcher: this.dispatcher,
      assets: this.model.unusedAssets
    });
    this.lastSavedView = new storybase.builder.views.LastSavedView({
      dispatcher: this.dispatcher,
      lastSaved: this.model.get('last_edited')
    });

    this.model.on("sync", this.triggerSaved, this);
    this.model.sections.on("reset", this.triggerReady, this);
    this.model.unusedAssets.on("sync reset add", this.hasAssetList, this);

    this.dispatcher.on("select:template", this.setStoryTemplate, this);
    this.dispatcher.on("ready:templateSections", this.initializeStoryFromTemplate, this);
    this.dispatcher.on("do:save:story", this.save, this);
    this.dispatcher.on("toggle:assetlist", this.toggleAssetList, this);
    this.dispatcher.on("add:sectionasset", this.showSaved, this);
    this.dispatcher.on("save:section", this.showSaved, this);
    this.dispatcher.on("save:story", this.showSaved, this);
    this.dispatcher.on("ready:story", this.createEditViews, this);
    this.dispatcher.on("created:section", this.handleCreateSection, this);

    _.bindAll(this, 'setTemplateStory', 'setTemplateSections', 'createSectionEditView');

    if (!this.model.isNew()) {
      this.model.sections.fetch();
      this.model.unusedAssets.fetch();
    }
  },

  triggerReady: function() {
    this.dispatcher.trigger('ready:story', this.model);
  },

  handleCreateSection: function(section) {
    var view = this.createSectionEditView(section);
    this.dispatcher.trigger('select:section', section);
    // TODO: Figure out how to show editor for newly created 
    // BOOKMARK
  },

  createSectionEditView: function(section) {
    var view = new storybase.builder.views.SectionEditView({
      dispatcher: this.dispatcher,
      model: section,
      story: this.model,
      assetTypes: this.options.assetTypes,
      layouts: this.options.layouts
    }); 
    this.sectionListView.$el.before(view.render().$el.hide());
    return view;
  },

  createEditViews: function() {
    console.debug("Entering createEditViews");
    var storyEditView = new storybase.builder.views.StoryInfoEditView({
      dispatcher: this.dispatcher,
      help: this.help.where({slug: 'story-information'})[0],
      model: this.model
    });
    var callEditView = new storybase.builder.views.CallToActionEditView({
      dispatcher: this.dispatcher,
      help: this.help.where({slug: 'call-to-action'})[0],
      model: this.model
    });
    this.sectionListView.$el.before(storyEditView.render().$el.hide());
    this.model.sections.each(this.createSectionEditView); 
    this.sectionListView.$el.before(callEditView.render().$el.hide());
    storyEditView.show();
  },

  render: function() {
    console.info('Rendering builder view');
    var that = this;
    this.$el.prepend(this.unusedAssetView.render().$el.hide());
    this.$el.prepend(this.lastSavedView.render().el);
    this.$el.append(this.sectionListView.render().el);
    return this;
  },

  /**
   * Event callback that displays an alert indicating the story has been
   * saved.
   */
  showSaved: function(model, showAlert) {
    showAlert = _.isUndefined(showAlert) || showAlert;
    if (showAlert) {
      this.dispatcher.trigger('alert', 'success', "The story has been saved");
    }
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
    this.model.set('summary',
                   this.templateStory.get('summary'));
    this.model.set('call_to_action',
                   this.templateStory.get('call_to_action'));
    this.templateSections.each(function(section) {
      var sectionCopy = new storybase.models.Section();
      sectionCopy.set("title", section.get("title"));
      sectionCopy.set("layout", section.get("layout"));
      sectionCopy.set("root", section.get("root"));
      sectionCopy.set("weight", section.get("weight"));
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
        that.dispatcher.trigger('navigate', model.id + '/', {
          trigger: false 
        });
        model.saveSections();
      }
    });
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
  },

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

storybase.builder.views.RichTextEditorMixin = {
  toolbarTemplateSource: $('#editor-toolbar-template').html(),

  getEditorToolbarHtml: function() {
    return this.toolbarTemplateSource; 
  },

  getEditorToolbarEl: function() {
    if (_.isUndefined(this._editorToolbarEl)) {
      this._editorToolbarEl = $(this.getEditorToolbarHtml())[0];
    }
    return this._editorToolbarEl; 
  },

  getEditor: function(el, callbacks) {
    var defaultCallbacks = {
      'focus': function() {
        $(this.toolbar.container).show();
      },

      'blur': function() {
        if (this._okToHideToolbar) {
          $(this.toolbar.container).hide();
        }
      },

      'load': function() {
        var that = this;
        this._okToHideToolbar = true;
        $(this.toolbar.container).hide();
        $(this.toolbar.container).mouseover(function() {
          that._okToHideToolbar = false;
        });
        $(this.toolbar.container).mouseout(function() {
          that._okToHideToolbar = true;
        });
      }

    };
    var editor;
    var toolbarEl = this.getEditorToolbarEl();
    $(el).before(toolbarEl);
    editor = new wysihtml5.Editor(
      el,    
      {
        toolbar: toolbarEl, 
        parserRules: wysihtml5ParserRules
      }
    );
    callbacks = _.isUndefined(callbacks) ? {} : callbacks;
    _.defaults(callbacks, defaultCallbacks);
    _.each(callbacks, function(value, key, list) {
      editor.on(key, value);
    });
    return editor;
  }
};

// TODO: Rename this ThumbnailSelectMixin
storybase.builder.views.ThumbnailHighlightMixin = {
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
  },

  isHighlighted: function() {
    return this.$el.hasClass(this.highlightClass);
  }
};

storybase.builder.views.SectionListView = Backbone.View.extend({
  tagName: 'ul',

  className: 'sections',

  events: {
    'click .spacer': 'clickSpacer',
    'sortupdate': 'handleSort'
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.model = this.options.model;
    this._thumbnailViews = {};
    this._sortedThumbnailViews = [];
    this._sectionsFetched = false;
    this._thumbnailsAdded = false;

    this.dispatcher.on("do:remove:section", this.removeSection, this);
    this.dispatcher.on("ready:story", this.addSectionThumbnails, this);

    _.bindAll(this, 'addSectionThumbnail');
  },

  addSectionThumbnail: function(section, index) {
    var view = new storybase.builder.views.SectionThumbnailView({
      dispatcher: this.dispatcher,
      model: section
    });
    index = _.isUndefined(index) ? this._sortedThumbnailViews.length - 1 : index + 1; 
    console.info("Adding section thumbnail at index " + index);
    this._sortedThumbnailViews.splice(index, 0, view);
    this._thumbnailViews[section.id] = view;
    return view;
  },

  addStoryInfoThumbnail: function() {
    var view = new storybase.builder.views.PseudoSectionThumbnailView({
      dispatcher: this.dispatcher,
      title: "Story Information",
      pseudoSectionId: 'story-info'
    });
    this._sortedThumbnailViews.push(view);
    this._thumbnailViews[view.pseudoSectionId] = view;
  },

  addCallToActionThumbnail: function() {
    var view = new storybase.builder.views.PseudoSectionThumbnailView({
      dispatcher: this.dispatcher,
      title: "Call to Action",
      pseudoSectionId: 'call-to-action'
    });
    this._sortedThumbnailViews.push(view);
    this._thumbnailViews[view.pseudoSectionId] = view;
  },

  /**
   * Event handler for when the story model and sections are ready.
   *
   * The story will either be ready when it has been cloned from the
   * template or when it has been fetched from the server.
   */
  addSectionThumbnails: function(options) {
    options = _.isUndefined(options) ? {} : options;
    _.defaults(options, {
      render: true
    });
    console.debug('Entering addSectionThumbnails');
    this.addStoryInfoThumbnail();
    this.addCallToActionThumbnail();
    this.model.sections.each(this.addSectionThumbnail);
    this._thumbnailsAdded = true;
    if (options.render) {
      this.render();
    }
  },

  render: function() {
    var i = 0;
    var numThumbnails;
    var thumbnailView;
    numThumbnails = this._sortedThumbnailViews.length;
    if (numThumbnails) {
      for (i = 0; i < numThumbnails; i++) {
        thumbnailView = this._sortedThumbnailViews[i];
        this.$el.append(thumbnailView.render().el);
      }
      this.dispatcher.trigger("select:thumbnail", this._sortedThumbnailViews[0]);
      this.$el.sortable({
        items: 'li:not(.pseudo)'
      });
    }

    return this;
  },

  getThumbnailView: function(section) {
    return this._thumbnailViews[section.id];
  },

  removeThumbnailView: function(view) {
    var index = _.indexOf(this._sortedThumbnailViews, view);
    if (view.isHighlighted()) {
      // Trying to remove the currently active view. Switch to
      // a different one before removing the elements.
      this.dispatcher.trigger('select:thumbnail', this._sortedThumbnailViews[index - 1]);
    }
    view.close();
    this._sortedThumbnailViews.splice(index, 1);
    if (_.isUndefined(view.pseudoSectionId)) {
      delete this._thumbnailViews[view.model.id];
    }
    else {
      delete this._thumbnailViews[view.pseudoSectionId];
    }
    this.dispatcher.trigger('remove:thumbnail', view);
  },

  removeSection: function(section) {
    // BOOKMARK
    console.debug("Removing section " + section.get("title"));
    var view = this.getThumbnailView(section);
    var handleSuccess = function(section, response) {
      section.deleted = true;
      this.removeThumbnailView(view);
    };
    var handleError = function(section, response) {
      this.dispatcher.trigger('error', gettext("Error removing section"));
    };
    handleSuccess = _.bind(handleSuccess, this); 
    handleError = _.bind(handleError, this); 
    if (this.model.sections.length > 1) {
      section.destroy({
        success: handleSuccess,
        error: handleError
      });
    }
    else {
      this.dispatcher.trigger('error', 
        gettext("You must have at least one section")
      );
    }
  },

  /**
   * Event callback for when a spacer between the section thumbnails is clicked.
   *
   * Initiates adding a section.
   */
  clickSpacer: function(evt) {
    evt.stopPropagation(); 
    var index = $(evt.currentTarget).data('index');
    this.addNewSection(index);
  },

  // BOOKMARK
  addNewSection: function(index) {
    // TODO: Default help for new section
    // TODO: Better method of selecting layout for new section.  This one
    // breaks if you remove all sections
    var section = new storybase.models.Section({
      title: gettext('New Section'),
      layout: this.model.sections.at(0).get('layout')
    });
    var postSave = function(section) {
      var thumbnailView;
      section.off('sync', postSave);
      this.dispatcher.trigger("created:section", section, index);
      thumbnailView = this.addSectionThumbnail(section, index);
      this.render();
      this.dispatcher.trigger('select:thumbnail', thumbnailView);
    };
    postSave = _.bind(postSave, this);
    this.model.sections.add(section, {at: index});
    section.on('sync', postSave);
    this.model.saveSections();
  },

  handleSort: function(evt, ui) {
    console.debug('Handling sort');
    var that = this;
    var sortedIds = this.$el.sortable('toArray');
    this._sortedThumbnailViews = [];
    var addView = _.bind(function(id) {
      this._sortedThumbnailViews.push(this._thumbnailViews[id]);
    }, this);
    this._sortedThumbnailViews.push(this._thumbnailViews['story-info']);
    _.each(sortedIds, addView);
    this._sortedThumbnailViews.push(this._thumbnailViews['call-to-action']);
    this.model.sections.sortByIdList(sortedIds);
    this.model.saveSections();
  }

});

storybase.builder.views.SectionThumbnailView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.ThumbnailHighlightMixin, {
    tagName: 'li',

    className: 'section-thumbnail-container',

    templateSource: $('#section-thumbnail-template').html(),

    events: {
      "click .section-thumbnail": "select",
      "click .remove": "clickRemove"
    },

    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      this.template = Handlebars.compile(this.templateSource);
      this.editView = this.options.editView;
      this._selected = false;


      this.dispatcher.on("select:thumbnail", this.highlight, this);
      this.dispatcher.on("remove:thumbnail", this.render, this);
      this.model.on("change", this.render, this);
      this.model.on("sync", this.render, this);
    },

    /**
     * Cleanup the view.
     */
    close: function() {
      this.remove();
      this.undelegateEvents();
      this.unbind();
      this.dispatcher.off("select:thumbnail", this.highlight, this);
      this.dispatcher.off("remove:thumbnail", this.render, this);
      this.model.off("change", this.render);
      this.model.off("sync", this.render, this);
    },

    render: function() {
      var index = this.model.collection.indexOf(this.model);
      var nextIndex = (index == this.model.collection.length - 1) ? index + 1 : null;
      var context = _.extend({
          id: this.model.id,
          isNew: this.model.isNew(),
          index: this.model.isNew() ? false : index.toString(),
          nextIndex: this.model.isNew() ? false: nextIndex
        },
        this.model.toJSON()
      );
      this.$el.attr('id', this.model.id);
      this.$el.html(this.template(context));
      this.delegateEvents();
      return this;
    },

    select: function() {
      console.info("Clicked thumbnail for section " + this.model.get('title'));
      this.dispatcher.trigger("select:thumbnail", this);
      this.dispatcher.trigger("select:section", this.model);
    },

    clickRemove: function(evt) {
      evt.preventDefault();
      evt.stopPropagation();
      this.dispatcher.trigger("do:remove:section", this.model);
    }
}));

storybase.builder.views.PseudoSectionThumbnailView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.ThumbnailHighlightMixin, {
    tagName: 'li',

    className: 'section-thumbnail-container pseudo',

    templateSource: $('#section-thumbnail-template').html(),

    events: {
      "click": "select"
    },

    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      this.pseudoSectionId = this.options.pseudoSectionId;
      this.title = this.options.title;
      this.template = Handlebars.compile(this.templateSource);
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
      this.dispatcher.trigger('select:section', this.pseudoSectionId);
    }
}));

storybase.builder.views.PseudoSectionEditView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.RichTextEditorMixin, {
    tagName: 'div',

    defaults: {},

    initialize: function() {
      _.defaults(this.options, this.defaults);
      this.dispatcher = this.options.dispatcher;
      this.help = this.options.help;
      this.template = Handlebars.compile(this.templateSource);

      this.dispatcher.on('select:section', this.show, this);
      console.debug("Initializing edit view for " + this.pseudoSectionId);
    },

    show: function(id) {
      id = _.isUndefined(id) ? this.pseudoSectionId : id;
      if (id == this.pseudoSectionId) {
        console.debug("Showing editor for pseduo-section " + this.pseudoSectionId);
        this.$el.show();
        this.dispatcher.trigger('do:show:help', false, this.help.toJSON()); 
      }
      else {
        console.debug("Hiding editor for pseduo-section " + this.pseduoSectionId);
        this.$el.hide();
      }
      return this;
    },

    saveAttr: function(key, value) {
      if (_.has(this.model.attributes, key)) {
        this.model.set(key, value);
        if (this.model.isNew()) {
          this.dispatcher.trigger("do:save:story");
        }
        else {
          this.model.save();
        }
        console.info("Updated " + key + " to " + value);
      }
    },

    /**
     * Event handler for when form elements are changed
     */
    change: function(e) {
      var key = $(e.target).attr("name");
      var value = $(e.target).val();
      this.saveAttr(key, value);
    }
  })
);

/**
 * View for editing story metadata
 */
storybase.builder.views.StoryInfoEditView = storybase.builder.views.PseudoSectionEditView.extend({ 

  className: 'edit-story-info edit-section',

  pseudoSectionId: 'story-info',

  templateSource: $('#story-info-edit-template').html(),

  events: function() {
    var events = {};
    events['change ' + this.options.summaryEl] = 'change';
    return events;
  },

  defaults: {
    titleEl: '.title',
    bylineEl: '.byline',
    summaryEl: 'textarea[name="summary"]' 
  },

  render: function() {
    console.debug('Rendering story information editor');
    var that = this;
    var handleChange = function () {
      // Trigger the change event on the underlying element 
      that.$(that.options.summaryEl).trigger('change');
    };
    var editableCallback = function(value, settings) {
      that.saveAttr($(this).data("input-name"), value);
      return value;
    };
    this.$el.html(this.template(this.model.toJSON()));
    // Initialize wysihmtl5 editor
    this.summaryEditor = this.getEditor(
      this.$(this.options.summaryEl)[0],
      {
        change: handleChange
      }
    );
      
    this.$(this.options.titleEl).editable(editableCallback, {
      placeholder: gettext('Click to edit title'),
      tooltip: gettext('Click to edit title')
    });
    this.$(this.options.bylineEl).editable(editableCallback, {
      placeholder: gettext('Click to edit byline'),
      tooltip: gettext('Click to edit byline')
    });
    return this;
  }
});

/**
 * View for editing the story's call to action 
 */
storybase.builder.views.CallToActionEditView = storybase.builder.views.PseudoSectionEditView.extend({ 
  className: 'edit-call-to-action edit-section',

  // The section edit views can be identified by the ID of their
  // sections, but these pseudo-section edit views need an
  // explicit identifier
  pseudoSectionId: 'call-to-action',

  defaults: {
    callToActionEl: 'textarea[name="call_to_action"]'
  },

  templateSource: $('#story-call-to-action-edit-template').html(),

  events: function() {
    var events = {};
    events['change ' + this.options.callToActionEl] = 'change';
    return events;
  },

  render: function() {
    var that = this;
    var handleChange = function () {
      // Trigger the change event on the underlying element 
      that.$(that.options.callToActionEl).trigger('change');
    };
    this.$el.html(this.template(this.model.toJSON()));
    // Add the toolbar elemebt for the wysihtml5 editor
    // Initialize wysihmtl5 editor
    this.callEditor = this.getEditor(
      this.$(this.options.callToActionEl)[0],
      {
        change: handleChange
      }
    );
    return this;
  }
});

/**
 * View for editing a section
 */
storybase.builder.views.SectionEditView = Backbone.View.extend({
  tagName: 'div',

  className: 'edit-section',

  templateSource: $('#section-edit-template').html(),

  defaults: {
    titleEl: '.title'
  },

  events: {
    "change input": 'change',
    "change select.layout": 'change'
  },

  initialize: function() {
    _.defaults(this.options, this.defaults);
    this.dispatcher = this.options.dispatcher;
    this.story = this.options.story;
    this.layouts = this.options.layouts;
    this.templateSource = this.options.templateSource || this.templateSource;
    this.template = Handlebars.compile(this.templateSource);
    this.assets = this.options.assets || new storybase.collections.SectionAssets();
    this._unsavedAssets = [];
    this._doConditionalRender = false;
    this._firstSave = this.model.isNew();

    _.bindAll(this, 'renderAssetViews');
    this.dispatcher.on('do:add:sectionasset', this.addAsset, this);
    this.dispatcher.on('do:remove:sectionasset', this.removeAsset, this);
    this.dispatcher.on('select:section', this.show, this);
    this.model.on("change:layout", this.changeLayout, this);
    this.model.on("sync", this.saveSectionAssets, this);
    this.model.on("sync", this.conditionalRender, this);
    this.model.on("sync", this.triggerSaved, this);
    this.model.on("destroy", this.handleDestroy, this);
    this.assets.on("reset sync", this.renderAssetViews, this);
  },

  close: function() {
    this.remove();
    this.undelegateEvents();
    this.unbind();
    this.dispatcher.off('do:add:sectionasset', this.addAsset, this);
    this.dispatcher.off('do:remove:sectionasset', this.removeAsset, this);
    this.dispatcher.off('select:section', this.show, this);
    this.model.off("change:layout", this.changeLayout, this);
    this.model.off("sync", this.saveSectionAssets, this);
    this.model.off("sync", this.conditionalRender, this);
    this.model.off("sync", this.triggerSaved, this);
    this.model.off("destroy", this.handleDestroy, this);
    this.assets.off("reset sync", this.renderAssetViews, this);
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
        section: that.model, 
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
    var that = this;
    var context = this.model.toJSON();
    var editableCallback = function(value, settings) {
      that.saveAttr($(this).data("input-name"), value);
      return value;
    };
    context.layouts = this.getLayoutContext();
    this.$el.html(this.template(context));
    if (this.model.isNew()) {
      this.renderAssetViews();
    }
    else {
      this.assets.url = this.model.url() + 'assets/';
      this.assets.fetch();
    }
    this.$(this.options.titleEl).editable(editableCallback, {
      placeholder: gettext('Click to edit title'),
      tooltip: gettext('Click to edit title')
    });
    return this;
  },

  show: function(section) {
    section = _.isUndefined(section) ? this.model : section;
    if (section == this.model) {
      console.debug('showing section ' + section.get('title'));
      this.$el.show();
      this.dispatcher.trigger('do:show:help', false, 
                              this.model.get('help')); 
    }
    else {
      if (_.isObject(section)) {
        console.debug('hiding section ' + section.get('title'));
      }
      else {
        console.debug("hiding pseudo-section " + section);
      }
      this.$el.hide();
    }
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

  saveAttr: function(key, value) {
    if (_.has(this.model.attributes, key)) {
      this.model.set(key, value);
      if (this.model.isNew()) {
        this.dispatcher.trigger("do:save:story");
      }
      else {
        this.model.save();
      }
      console.info("Updated " + key + " to " + value);
    }
  },

  /**
   * Event handler for when form elements are changed
   */
  change: function(e) {
    var key = $(e.target).attr("name");
    var value = $(e.target).val();
    this.saveAttr(key, value);
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
  addAsset: function(section, asset, container) {
    if (section == this.model) {
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
    this.dispatcher.trigger('save:section', this.model, !this._firstSave);
    this._firstSave = false;
  },

  handleDestroy: function() {
    console.debug("Section is being destroyed!");
    var triggerUnused = function(asset) {
      this.dispatcher.trigger("remove:sectionasset", asset);
    };
    triggerUnused = _.bind(triggerUnused, this);
    if (this.assets.length) {
      this.assets.each(triggerUnused);
      this.dispatcher.trigger('alert', 'info', gettext("The assets in the section you removed aren't gone forever.  You can re-add them from the asset list"));
    }
    if (this.$el.is(':visible')) {
      // Destroying the currently active view
      var index = this.model.collection.indexOf(this.model);
      console.debug('Destroying active view with index ' + index);
      if (index) {
        // If this isn't the first section, make the previous section
        // the active one
        this.dispatcher.trigger('select:section', this.model.collection.at(index - 1));
      }
      else {
        // Otherwise, show the story info section
        this.dispatcher.trigger('select:section', 'story-info');
      }
    }
    this.close();
  }
});

storybase.builder.views.SectionAssetEditView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.RichTextEditorMixin, {
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
      this.section = this.options.section;
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
      var context = {
        assetTypes: this.assetTypes
      };
      var editableCallback = function(value, settings) {
        that.saveAttr($(this).data("input-name"), value);
        return value;
      };
      var state = this.getState();
      this.template = Handlebars.compile(this.templateSource());
      if (state === 'display') {
        context.model = this.model.toJSON()
      }
      this.$el.html(this.template(context));
      if (state === 'edit') {
        this.form.render().$el.append('<input type="reset" value="Cancel" />').append('<input type="submit" value="Save" />');
        if (_.has(this.form.fields, 'body')) {
          this.bodyEditor = this.getEditor(
            this.form.fields.body.editor.el
          );
        }
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
            that.dispatcher.trigger("do:add:sectionasset", that.section,
              that.model, that.container
            );
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
  })
);

storybase.builder.views.DataView = Backbone.View.extend({
  templateSource: $('#data-template').html(),

  events: {
    'click .add-dataset': 'showForm',
    'click .cancel': 'hideForm',
    'click .delete-dataset': 'handleDelete',
    'submit form': 'processForm'
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);

    this.collection = new storybase.collections.DataSets;
    if (_.isUndefined(this.model)) {
      this.dispatcher.on("ready:story", this.setStory, this);
    }
    else {
      this.collection.setStory(this.model);
    }
    this.collection.on('reset', this.render, this);
    this._collectionFetched = false;

    this.form = new Backbone.Form({
      schema: storybase.models.DataSet.prototype.schema
    }); 
  },

  setStory: function(story) {
    this.model = story;
    this.collection.setStory(this.model);
  },

  fetchCollection: function() {
    var that = this;
    this.collection.fetch({
      success: function() {
        that._collectionFetched = true;
      }
    });
  },

  render: function() {
    console.info('Rendering data view');
    if (!this._collectionFetched) {
      this.fetchCollection();
    }
    var context = {
      datasets: this.collection.toJSON()
    };
    this.$el.html(this.template(context));
    this.$('.add-dataset').before(this.form.render().$el.append('<input class="cancel" type="reset" value="Cancel" />').append('<input type="submit" value="Save" />').hide());
    this.delegateEvents();
    return this;
  },

  showForm: function(evt) {
    evt.preventDefault();
    this.form.$el.show();
    this.$('.add-dataset').hide();
  },

  hideForm: function(evt) {
    evt.preventDefault();
    this.form.$el.hide();
    this.$('.add-dataset').show();
  },

  processForm: function(evt) {
    evt.preventDefault();
    var that = this;
    var errors = this.form.validate();
    if (!errors) {
      var formData = this.form.getValue();
      if (formData.file) {
        formData.filename = formData.file;
        this.form.fields.file.editor.getValueAsDataURL(function(dataURL) {
          formData.file = dataURL;
          that.addDataSet(formData);
        });
      }
      else {
        this.addDataSet(formData);
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

  addDataSet: function(attrs) {
    var that = this;
    this.collection.create(attrs, {
      success: function(model, response) {
        that.trigger('save:dataset', model);
        that.dispatcher.trigger('alert', 'success', "Data set added");
        that.render();
      },
      error: function(model, response) {
        that.dispatcher.trigger('error', 'Error saving the data set');
      }
    });
  },

  handleDelete: function(evt) {
    evt.preventDefault();
    var that = this;
    var datasetId = $(evt.target).data('dataset-id');
    var dataset = this.collection.get(datasetId);
    dataset.destroy({
      success: function(model, response) {
        that.dispatcher.trigger('delete:dataset', model);
        that.dispatcher.trigger('alert', 'success', "Data set deleted");
        that.render();
      },
      error: function(model, response) {
        that.dispatcher.trigger('error', 'Error removing the data set');
      }
    });
  },
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
    'click .publish': 'handlePublish'
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
  },

  render: function() {
    console.info('Rendering share view');
    var context = {};
    this.$el.html(this.template(context));
    this.delegateEvents();
    return this;
  },

  handlePublish: function(evt) {
    evt.preventDefault();
    console.debug('Entering handlePublish');
    var that = this;
    var triggerPublished = function(model, response) {
      that.dispatcher.trigger('publish:story', model);
      that.dispatcher.trigger('alert', 'success', 'Story published');
    };
    var triggerError = function(model, response) {
      that.dispatcher.trigger('error', "Error publishing story");
    };
    this.model.save({'status': 'published'}, {
      success: triggerPublished, 
      error: triggerError 
    });
  }
});
