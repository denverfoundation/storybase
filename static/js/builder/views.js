Namespace('storybase.builder.views');
Namespace.use('storybase.utils.capfirst');
Namespace.use('storybase.utils.geocode');

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
 *
 * TODO: Document the options for this view
 *
 */
storybase.builder.views.AppView = Backbone.View.extend({
  initialize: function() {
    // Common options passed to sub-views
    var commonOptions = {
      startOverUrl: this.options.startOverUrl,
      visibleSteps: this.options.visibleSteps
    };
    var buildViewOptions;
    this.dispatcher = this.options.dispatcher;
    commonOptions.dispatcher = this.dispatcher;
    // The currently active step of the story building process
    // This will get set by an event callback 
    this.activeStep = null; 

    // Initialize a view for the tools menu
    this.toolsView = new storybase.builder.views.ToolsView(commonOptions);
    // TODO: Change the selector as the template changes
    this.$('header').first().children().first().append(this.toolsView.el);

    this.helpView = new storybase.builder.views.HelpView(commonOptions);

    if (this.model) {
      commonOptions.model = this.model;
    }

    // Initialize the view for the workflow step indicator
    this.workflowStepView = new storybase.builder.views.WorkflowStepView(
      commonOptions
    );
    // TODO: Change the selector as the template changes
    this.$('header').first().children().first().append(this.workflowStepView.el);

    buildViewOptions = _.defaults({
      assetTypes: this.options.assetTypes,
      containerTemplates: this.options.containerTemplates,
      layouts: this.options.layouts,
      help: this.options.help,
      prompt: this.options.prompt,
      relatedStories: this.options.relatedStories,
      templateStory: this.options.templateStory,
      showStoryInformation: this.options.showStoryInformation,
      showCallToAction: this.options.showCallToAction,
      showSectionList: this.options.showSectionList,
      showLayoutSelection: this.options.showLayoutSelection,
      showSectionTitles: this.options.showSectionTitles,
      showStoryInfoInline: this.options.showStoryInfoInline,
      showTour: this.options.showTour
    }, commonOptions);

    // Store subviews in an object keyed with values of this.activeStep
    this.subviews = {
      selecttemplate: new storybase.builder.views.SelectStoryTemplateView({
        dispatcher: this.dispatcher,
        collection: this.options.storyTemplates
      }),
    };

    // Create views for additional workflow steps if they're enabled
    // in options. We don't iterate through the steps because the
    // views use different constructor, options. If this gets to
    // unwieldy, maybe use a factory function.
    if (this.options.visibleSteps.data) {
      this.subviews.data = new storybase.builder.views.DataView(commonOptions);
    }
    if (this.options.visibleSteps.tag) {
      this.subviews.tag =  new storybase.builder.views.TaxonomyView(
        _.defaults({
          places: this.options.places,
          topics: this.options.topics,
          organizations: this.options.organizations,
          projects: this.options.projects
        }, commonOptions)
      );
    }
    if (this.options.visibleSteps.review) {
      this.subviews.review = new storybase.builder.views.ReviewView(commonOptions);
    }
    if (this.options.visibleSteps.publish) {
      this.subviews.publish =  new storybase.builder.views.PublishView(
        _.defaults({
          showSharing: this.options.showSharing
        }, commonOptions)
      );
    }

    // IMPORTANT: Create the builder view last because it triggers
    // events that the other views need to listen to
    this.subviews.build = new storybase.builder.views.BuilderView(buildViewOptions);

    // Initialize the properties that store the last alert level
    // and message.
    this.lastLevel = null;
    this.lastMessage = null;

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
    this.dispatcher.trigger("select:workflowstep", 'build');
  },

  /**
   * Set the active step of the workflow and re-render the view
   */
  updateStep: function(step) {
    // Checking that step is different from the active step is
    // required for the initial saving of the story.  The active view
    // has already been changed by ``this.setTemplate`` so we don't
    // want to re-render.  In all other cases the changing of the 
    // active view is initiated by the router triggering the ``select:
    // workflowstep`` signal
    if (this.activeStep != step) {
      console.debug('Updating active step to ' + step);
      this.activeStep = step;
      this.render();
    }
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
    var activeNavView = _.isUndefined(activeView.getNavView) ? null: activeView.getNavView();
    if (activeNavView) {
      this.$('#nav-container').empty();
      this.$('#nav-container').append(activeNavView.el);
      activeNavView.$el.addClass('container');
    }
    this.$('#app').empty();
    this.$('#app').append(activeView.render().$el);
    // Some views have things that only work when the element has been added
    // to the DOM. The pattern for handling this comes courtesy of
    // http://stackoverflow.com/questions/9350591/backbone-using-jquery-plugins-on-views
    if (activeView.onShow) {
      activeView.onShow();
    }
    if (this.workflowStepView) {
      this.workflowStepView.render();
    }
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
    var $el = this.$('.alerts');
    var newTop;
    var numAlerts = $el.children().length;
    var view = new storybase.builder.views.AlertView({
      level: level,
      message: msg
    });
    // Check for duplicate messages and only show the message
    // if it's different.
    if (!(level === this.lastLevel && msg === this.lastMessage && numAlerts > 0)) {
      newTop = this.$('#nav-container').offset().top + this.$('#nav-container').outerHeight();
      $el.css('top', newTop);
      $el.prepend(view.render().el);
      view.$el.fadeOut(15000, function() {
        $(this).remove();
      });
    }
    this.lastLevel = level;
    this.lastMessage = msg;
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
    // If the cookie is set, use the stored value.
    // Otherwise, default to true.
    this.autoShow = $.cookie('storybase_show_builder_help') === 'false' ? false : true;

    this.dispatcher.on('do:show:help', this.show, this);
    this.dispatcher.on('do:set:help', this.set, this);
    this.dispatcher.on('do:hide:help', this.hide, this);
  },

  setAutoShow: function(evt) {
    this.autoShow = $(evt.target).prop('checked'); 
    $.cookie("storybase_show_builder_help", this.autoShow, {path: '/'});
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

  hide: function() {
    $.modal.close();
  },

  set: function(help) {
    this.help = help;
  },

  render: function() {
    var context = _.extend({
      'autoShow': this.autoShow
    }, this.help);
    this.$el.html(this.template(context));
    return this;
  }
});

/**
 * Base class for views that represent a list of items that trigger
 * some action when clicked.
 */
storybase.builder.views.ClickableItemsView = Backbone.View.extend({
  items: [],

  itemTemplateSource: $('#clickable-item-template').html(),

  getItemTemplate: function() {
    if (_.isUndefined(this.itemTemplate)) {
      this.itemTemplate = Handlebars.compile(this.itemTemplateSource);
    }
    return this.itemTemplate; 
  },

  events: function() {
    var items = _.result(this, 'items');
    var events = {};
    _.each(items, function(item) {
      if (item.callback) {
        events["click ." + item.id] = item.callback;
      }
    });
    return events;
  },

  getItem: function(id) {
    var items = _.result(this, 'items');
    return _.filter(items, function(item) {
      return item.id === id;
    })[0];
  },

  setVisibility: function(id, visible) {
    var item = this.getItem(id);
    item.visible = visible;
  },

  /**
   * Get the value of a property of an item
   *
   * @param {Object} item Clickable item from this.items
   * @param {String} property Property of item whose value should be fetched
   * @param {Mixed} [defaultVal=true] Default value to return if property
   *  is undefined
   * @returns {Mixed} Value of property or defaultVal if property is undefined
   *
   * If the property value is a string, it tries to call a method of that name
   * on this view instance and return that value.  Otherwise, it returns the
   * value of the property or the return value of a call to the property if 
   * it is a function.
   */
  getPropertyValue: function(item, property, defaultVal) {
    defaultVal = _.isUndefined(defaultVal) ? true : defaultVal;
    if (_.isUndefined(item[property])) {
      // Property is undefined, return the default value 
      return defaultVal; 
    }
    else if (_.isString(item[property])) {
      // Visible property is a string, treat it as the name of a
      // property of this view and return its value. 
      return _.result(this, item[property]);
    }
    else {
      // Visible property is a property of the item object.
      // Return the value of that property.
      return _.result(item, property);
    }
  },

  getVisibleItems: function() {
    var items = _.result(this, 'items');
    return _.filter(items, function(item) {
      return this.getPropertyValue(item, 'visible', true);
    }, this);
  },

  getItemHref: function(itemOptions) {
    return _.isUndefined(itemOptions.path) ? '#' : itemOptions.path;
  },

  getItemClass: function(itemOptions) {
    var cssClass = "";
    var enabled = this.getPropertyValue(itemOptions, 'enabled', true);
    var selected = this.getPropertyValue(itemOptions, 'selected', false); 

    if (!enabled) {
      cssClass = cssClass + " disabled"; 
    }

    if (selected) {
      cssClass = cssClass + " selected";
    }

    return cssClass;
  },

  renderItem: function(itemOptions) {
    this.$el.append(this.itemTemplate({
      id: itemOptions.id,
      class: this.getItemClass(itemOptions),
      title: itemOptions.title,
      text: itemOptions.text,
      href: this.getItemHref(itemOptions)
    }));
  },

  extraRender: function() {},

  render: function() {
    this.$el.empty();
    _.each(this.getVisibleItems(), function(item) {
      this.renderItem(item);
    }, this);
    this.extraRender();
    this.delegateEvents();

    return this;
  }
});

/**
 * List of clickable items that navigate to different workflow
 * steps.
 */
storybase.builder.views.WorkflowNavView = storybase.builder.views.ClickableItemsView.extend({ 
  tagName: 'div',

  className: 'workflow-nav',

  itemTemplateSource: $('#workflow-nav-item-template').html(),

  items: [],

  events: function() {
    var events = {};
    var items = _.result(this, 'items');
    _.each(items, function(item) {
      if (item.route !== false) {
        events['click #' + item.id] = _.isUndefined(item.callback) ? this.handleClick : item.callback;
      }
    }, this);
    return events;
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.items = _.isUndefined(this.options.items) ? this.items : this.options.items;
    this.itemTemplateSource = _.isUndefined(this.options.itemTemplateSource) ? this.itemTemplateSource : this.options.itemTemplateSource;
    this.itemTemplate = this.getItemTemplate();
    // Include story ID in paths?  This should only happen for stories
    // created in this session.
    this._includeStoryId = _.isUndefined(this.model) || this.model.isNew();
    if (_.isUndefined(this.model)) {
      this.dispatcher.on("ready:story", this.setStory, this);
    }
    this.extraInit();
  },

  /**
   * Extra initialization operations
   *
   * Define this functionality in view subclasses.
   */
  extraInit: function() {
  },

  setStory: function(story) {
    this.model = story;
    this.dispatcher.on("save:story", this.handleInitialSave, this);
    this.render();
  },

  handleInitialSave: function(story) {
    this.dispatcher.off("save:story", this.handleInitialSave, this);
    this.render();
  },

  getItemHref: function(itemOptions) {
    path = itemOptions.path;
    if (itemOptions.route !== false) {
      if (!_.isUndefined(this.model) && this._includeStoryId) {
        path = this.model.id + '/' + path;
      }
      path = storybase.builder.globals.APP_ROOT + path;
    }
    return path;
  },


  handleClick: function(evt) {
    console.debug('handling click of navigation button');
    evt.preventDefault();
    var $button = $(evt.target);
    var item = this.getItem($button.attr('id'));
    var valid = _.isFunction(item.validate) ? item.validate() : true;
    var href;
    var route;
    if (!$button.hasClass("disabled") && valid) { 
      href = $button.attr("href");
      // Strip the base path of this app
      route = href.substr(storybase.builder.globals.APP_ROOT.length);
      this.dispatcher.trigger('navigate', route, 
        {trigger: true, replace: true});
    }
  },

  isStorySaved: function() {
    return _.isUndefined(this.model) ? false : !this.model.isNew();
  }
});

/**
 * Shows current step of workflow 
 */
storybase.builder.views.WorkflowStepView = storybase.builder.views.WorkflowNavView.extend({
  tagName: 'ul',

  className: 'workflow-step nav',

  itemTemplateSource: $('#workflow-item-template').html(),

  /**
   * Initialize items.
   *
   * Call this from initialize() once rather than repeating the logic
   * each time items() is called.
   */
  _initItems: function() {
    var items = [];
    if (this.options.visibleSteps.build) {
      items.push({
        id: 'build',
        title: gettext("Organize your thoughts, tell your story"),
        text: gettext("Build"),
        visible: true,
        selected: false,
        path: ''
      });
    }
    if (this.options.visibleSteps.data) {
      items.push({
        id: 'data',
        title: gettext("Add raw data for charts, tables, maps and other visualizations that you used in your story"),
        text: gettext('Add Data'),
        visible: 'isStorySaved',
        selected: false,
        path: 'data/'
      });
    }
    if (this.options.visibleSteps.tag) {
      items.push({
        id: 'tag',
        title: gettext("Help others discover your story"),
        text: gettext('Tag'),
        visible: 'isStorySaved',
        selected: false,
        path: 'tag/',
      });
    }
    if (this.options.visibleSteps.review) {
      items.push({
        id: 'review',
        title: gettext("Make sure your story is good to go"),
        text: gettext('Review'),
        visible: 'isStorySaved',
        selected: false,
        path: 'review/'
      });
    }
    if (this.options.visibleSteps.publish) {
      items.push({
        id: 'publish',
        title: gettext("Publish your story and share it with others"),
        text: gettext('Publish/Share'),
        visible: 'isStorySaved',
        selected: false,
        path: 'publish/'
      });
    }
    return items;
  },

  extraInit: function() {
    this.items = _.isUndefined(this.options.items) ? this._initItems() : this.options.items;
    this.activeStep = null;
    this.dispatcher.on("select:workflowstep", this.updateStep, this);
  },

  updateSelected: function() {
    _.each(this.items, function(item) {
      if (item.id === this.activeStep) {
        item.selected = true;
      }
      else {
        item.selected = false;
      }
    }, this);
  },

  updateStep: function(step) {
    this.activeStep = step;
    if (this.activeStep === 'selecttemplate') {
      this.activeStep = 'build';
    }
    this.updateSelected();
    this.render();
  },

  extraRender: function() {
    if (jQuery().tooltipster) {
      this.$('.tooltip').tooltipster({
        position: 'bottom'
      });
    }
  }
});

/**
 * Global tools menu.
 *
 * This includes things like "Help", "Exit"
 */
storybase.builder.views.ToolsView = storybase.builder.views.ClickableItemsView.extend({
  tagName: 'ul',

  className: 'tools nav',

  _initItems: function() {
    return [
      {
        id: 'help',
        title: gettext("Get help on the current story section"),
        text: gettext('Help'),
        callback: 'toggleHelp', 
        visible: true 
      },
      {
        id: 'assets',
        title: gettext("Show a list of assets you removed from your story"),
        text: gettext('Assets'),
        callback: 'toggleAssetList',
        visible: false
      },
      {
        id: 'preview',
        title: gettext("View your story in the story viewer (opens in a new window)"),
        text: gettext('Preview'),
        callback: 'previewStory',
        visible: false
      },
      {
        id: 'start-over',
        title: gettext("Leave your story in its current state and start a new story, with a new template"),
        text: gettext('Start Over'),
        path: this.options.startOverUrl,
        visible: false 
      },
      {
        id: 'exit',
        title: gettext("Leave the story builder and go to the home page"),
        text: gettext('Exit'),
        path: '/',
        visible: true 
      }
    ];
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.items = this._initItems();
    this.itemTemplate = this.getItemTemplate();
    this.activeStep = null;
    this.hasAssetList = false;

    this.dispatcher.on('has:assetlist', this.toggleAssetsItem, this);
    this.dispatcher.on('ready:story', this.handleStorySave, this);
    this.dispatcher.on('save:story', this.handleStorySave, this);
    this.dispatcher.on("select:workflowstep", this.updateStep, this);
  },

  toggleAssetsItem: function(hasAssetList) {
    this.hasAssetList = hasAssetList;
    this.setVisibility('assets', this.hasAssetList && this.activeStep === 'build');
    this.render();
  },

  previewStory: function(evt) {
    evt.preventDefault();
    var url = '/stories/' + this.storyId + '/viewer/';
    window.open(url);
  },

  toggleAssetList: function(evt) {
    evt.preventDefault();
    this.dispatcher.trigger("toggle:assetlist");
  },

  toggleHelp: function(evt) {
    evt.preventDefault();
    this.dispatcher.trigger('do:show:help', true);
  },
  
  handleStorySave: function(story) {
    if (!story.isNew() && _.isUndefined(this.storyId)) {
      var item = this.getItem('preview');
      this.storyId = story.id; 
      item.path = '/stories/' + this.storyId + '/viewer/';
      item.visible = true;
      this.render();
    }
  },

  updateVisible: function() {
    // The assets item should only be visible in the build Workflow
    // step
    if (this.activeStep === 'build') {
      this.setVisibility('assets', this.hasAssetList);
    }
    else {
      this.setVisibility('assets', false);
    }

    if (this.activeStep !== 'selecttemplate') {
      this.setVisibility('start-over', true);
    }
  },

  updateStep: function(step) {
    this.activeStep = step;
    this.updateVisible();
    this.render();
  },

  extraRender: function() {
    if (jQuery().tooltipster) {
      this.$('.tooltip').tooltipster({
        position: 'bottom'
      });
    }
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

  defaults: {
    titleEl: '.story-title'
  },

  initialize: function() {
    var that = this;
    var navViewOptions;
    var isNew = _.bind(function() {
      return !this.model.isNew();
    }, this)

    _.defaults(this.options, this.defaults);
    this.containerTemplates = this.options.containerTemplates;
    this.dispatcher = this.options.dispatcher;
    this.help = this.options.help;
    this._relatedStoriesSaved = false;

    if (_.isUndefined(this.model)) {
      // Create a new story model instance
      this.model = new storybase.models.Story({
        title: ""
      });
    }
    if (this.options.relatedStories) {
      this.model.setRelatedStories(this.options.relatedStories);
    }

    this.templateStory = this.options.templateStory;

    _.bindAll(this, 'createSectionEditView', 'simpleReview', 'setTemplateStory', 'initializeStoryFromTemplate');

    // Initialize navigation to the next workflow step
    navViewOptions = {
      model: this.model,
      dispatcher: this.dispatcher,
      items: []
    };
    // The next step will either be data (in the normal builder) or
    // publish (in the connected story builder). If this gets more
    // complicated, it might make more sense to have a global set
    // of items. 
    if (this.options.visibleSteps.data) {
      navViewOptions.items.push({
        id: 'workflow-nav-data-fwd',
        text: gettext("Add Data to Your Story"),
        path: 'data/',
        enabled: isNew 
      });
    }
    else if (this.options.visibleSteps.publish) {
      navViewOptions.items.push({
        id: 'workflow-nav-publish-fwd',
        text: gettext("Publish My Story"),
        path: 'publish/',
        enabled: isNew,
        validate: this.options.visibleSteps.review ? true : this.simpleReview
      });
    }
    this.navView = new storybase.builder.views.WorkflowNavView(navViewOptions);

    if (this.options.showSectionList) {
      this.sectionListView = new storybase.builder.views.SectionListView({
        dispatcher: this.dispatcher,
        navView: this.navView,
        model: this.model
      });
    }
    this.unusedAssetView = new storybase.builder.views.UnusedAssetView({
      dispatcher: this.dispatcher,
      assets: this.model.unusedAssets
    });
    this.lastSavedView = new storybase.builder.views.LastSavedView({
      dispatcher: this.dispatcher,
      lastSaved: this.model.get('last_edited')
    });

    this._editViews = [];

    this.model.on("sync", this.triggerSaved, this);
    this.model.sections.on("reset", this.triggerReady, this);
    this.model.unusedAssets.on("sync reset add", this.hasAssetList, this);

    this.dispatcher.on("select:template", this.setStoryTemplate, this);
    this.dispatcher.on("do:save:story", this.save, this);
    this.dispatcher.on("toggle:assetlist", this.toggleAssetList, this);
    this.dispatcher.on("add:sectionasset", this.showSaved, this);
    this.dispatcher.on("save:section", this.showSaved, this);
    this.dispatcher.on("save:story", this.showSaved, this);
    this.dispatcher.on("ready:story", this.createEditViews, this);
    this.dispatcher.on("save:story", this.setTitle, this);
    this.dispatcher.on("ready:story", this.setTitle, this);
    this.dispatcher.on("created:section", this.handleCreateSection, this);
    this.dispatcher.on("toggle:sectionlist", this.handleToggleSectionList, this);


    if (!this.model.isNew()) {
      this.model.sections.fetch();
      this.model.unusedAssets.fetch();
    }
    else if (this.templateStory) {
      // Model is new, but a template was provided when the builder was launched
      // We don't have to wait to request the template from the server.
      this.initializeStoryFromTemplate();
    }
  },

  triggerReady: function() {
    console.info('Story sections initialized');
    this.dispatcher.trigger('ready:story', this.model);
  },

  handleCreateSection: function(section) {
    var view = this.createSectionEditView(section);
    this.renderEditViews({showFirst: false});
    this.dispatcher.trigger('select:section', section);
  },

  createSectionEditView: function(section) {
    var options = {
      dispatcher: this.dispatcher,
      model: section,
      collection: this._editViews,
      story: this.model,
      assetTypes: this.options.assetTypes,
      layouts: this.options.layouts,
      containerTemplates: this.containerTemplates,
      defaultHelp: this.help.where({slug: 'new-section'})[0],
      showSectionTitles: this.options.showSectionTitles,
      showLayoutSelection: this.options.showLayoutSelection,
      showStoryInfoInline: this.options.showStoryInfoInline,
      prompt: this.options.prompt
    };
    var view;
    if (this.templateStory) {
      options.templateSection = this.templateStory.sections.get(section.get('template_section'));
    }
    view = new storybase.builder.views.SectionEditView(options);
    this._editViews.push(view);
    return view;
  },

  createEditViews: function() {
    var storyEditView = null;
    var callEditView = null;
    if (this.options.showStoryInformation) {
      storyEditView = new storybase.builder.views.StoryInfoEditView({
        dispatcher: this.dispatcher,
        help: this.help.where({slug: 'story-information'})[0],
        model: this.model
      });
      this._editViews.push(storyEditView);
    }
    this.model.sections.each(this.createSectionEditView); 
    if (this.options.showCallToAction) {
      callEditView = new storybase.builder.views.CallToActionEditView({
        dispatcher: this.dispatcher,
        help: this.help.where({slug: 'call-to-action'})[0],
        model: this.model
      });
      this._editViews.push(callEditView);
    }
    if (this.$el.is(':visible')) {
      this.renderEditViews();
    }
  },

  renderEditViews: function(options) {
    // TODO: Figure out if this is the best way to avoid showing the first
    // section each time the edit views are rendered.  It might make more sense
    // to put the call to ``this._editViews[0].show`` in an ``onShow`` event
    // for this view and call it upstream
    options = _.isUndefined(options) ? {} : options;
    _.defaults(options, {
      showFirst: true
    });
    var that = this;
    _.each(this._editViews, function(view) {
      that.$el.append(view.render().$el.hide());
    });
    if (this._editViews.length && options.showFirst) {
      //this._editViews[0].show();
      this.dispatcher.trigger('select:section', 'story-info');
    }
  },

  render: function() {
    console.info('Rendering builder view');
    var that = this;
    this.$el.prepend(this.unusedAssetView.render().$el.hide());
    if (this.sectionListView) {
      this.sectionListView.render();
    }
    if (this.navView) {
      this.navView.render();
    }
    this.renderEditViews();
    this.$el.append(this.lastSavedView.render().el);
    return this;
  },

  getNavView: function() {
    if (this.sectionListView) {
      return this.sectionListView;
    }
    else {
      return this.navView;
    }
  },

  /**
   * Things that need to happen after the view's element has
   * been added to the DOM.
   *
   * This is called from upstream views.
   */
  onShow: function() {
    // Recalculate the width of the section list view.
    var that = this;
    var showTour = _.isUndefined(guiders) ? false : ($.cookie('storybase_show_builder_tour') === 'false' ? false : true) && this.options.showTour;

    if (this.sectionListView) {
      this.sectionListView.setWidth();
    }
    
    if (showTour) { 
      guiders.createGuider({
        attachTo: '#toggle-section-list',
        buttons: [
          {
            name: gettext("Next"),
            onclick: guiders.next
          }
        ],
        position: 3,
        id: 'section-list-guider',
        title: gettext("Section List"),
        description: gettext("This bar shows a list of all the sections in the story. You can use it to select which section you want to edit, to add sections, and to remove sections"),
        next: 'section-thumbnail-guider'
      });
      guiders.createGuider({
        attachTo: '.section-thumbnail',
        buttons: [
          {
            name: gettext("Prev"),
            onclick: guiders.prev
          },
          {
            name: gettext("Next"),
            onclick: guiders.next
          }
        ],
        position: 2,
        id: 'section-thumbnail-guider',
        title: gettext("Select a Section"),
        description: gettext("Clicking on one of the sections will let you edit that section"),
        prev: 'section-list-guider',
        next: 'workflow-step-guider'
      });
      guiders.createGuider({
        attachTo: '.workflow-step #build',
        buttons: [
          {
            name: gettext("Prev"),
            onclick: guiders.prev
          },
          {
            name: gettext("Next"),
            onclick: guiders.next
          }
        ],
        position: 6,
        id: 'workflow-step-guider',
        title: gettext("Workflow Step"),
        description: gettext("Clicking on one of these tabs lets you switch between the different steps in the story building process"),
        next: 'help-guider'
      });
      guiders.createGuider({
        attachTo: '.tools .help',
        buttons: [
          {
            name: gettext("Prev"),
            onclick: guiders.prev
          },
          {
            name: gettext("Next"),
            onclick: guiders.next
          }
        ],
        position: 6,
        id: 'help-guider',
        title: gettext("Help"),
        description: gettext("Clicking the help button shows you help for the story section you're currently editing"),
        onShow: function() {
          that.dispatcher.trigger('do:show:help', true);
        },
        onHide: function() {
          that.dispatcher.trigger('do:hide:help', true);
        },
        next: 'tooltip-guider'
      });
      guiders.createGuider({
        attachTo: '.workflow-step #build',
        buttons: [
          {
            name: gettext("Close"),
            onclick: guiders.hideAll
          }
        ],
        position: 3,
        id: 'tooltip-guider',
        title: gettext("Tooltips"),
        description: gettext("You can find out more about many of the buttons and the links by hovering your mouse over the object"),
        onShow: function() {
          $('.workflow-step #build').triggerHandler('mouseover');
        },
        onHide: function() {
          // Set a cookie so the user doesn't see the builder tour again
          $.cookie("storybase_show_builder_tour", false, {path: '/'});
          $('.workflow-step #build').triggerHandler('mouseout');
        }
      });
      guiders.show('section-list-guider');
    }
  },

  getNavView: function() {
    if (this.sectionListView) {
      return this.sectionListView;
    }
    else {
      return this.navView;
    }
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
    this.templateStory.sections.on("reset", this.getContainerTemplates, this);
    this.templateStory.sections.fetch();
  },

  getContainerTemplates: function() {
    var that = this;
    this.templateStory.sections.off("reset", this.getContainerTemplates, this);
    this.containerTemplates.setTemplate(this.storyTemplate);
    this.containerTemplates.fetch({
      success: this.initializeStoryFromTemplate,
      error: function() {
        that.error(gettext("Failed fetching container templates"));
      }
    });
  },

  initializeStoryFromTemplate: function() {
    console.info("Initializing sections");
    this.model.fromTemplate(this.templateStory);
    this.dispatcher.trigger("ready:story", this.model);
  },

  save: function() {
    console.info("Saving story");
    var that = this;
    this.model.save(null, {
      success: function(model, response) {
        that.dispatcher.trigger('save:story', model);
        that.dispatcher.trigger('navigate', model.id + '/', {
          trigger: true 
        });
        model.saveSections();
        if (!that._relatedStoriesSaved) {
          model.saveRelatedStories();
        }
        // Re-render the navigation view to enable the button
        if (that.navView) {
          that.navView.render();
        }
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

  setTitle: function() {
    var title = this.model.get('title');
    if (title) {
      document.title = title + " | " + gettext("Floodlight Story Builder");
    }
  },

  getEditView: function(index) {
    return this._editViews[index];
  },

  /**
   * Do a simple review of the story.
   *
   * This is for the connected story builder.
   */
  simpleReview: function() {
    var editView = this.getEditView(0);
    // Stories must have titles
    if (!this.model.get('title')) {
      this.dispatcher.trigger('error', gettext("You must give your story a title"));
      this.$(this.options.titleEl).addClass('error');
      this.$(this.options.titleEl).triggerHandler('click');
      return false;
    }

    // All assets must be defined
    if (!editView.allAssetsDefined()) {
      this.dispatcher.trigger('error', gettext("You didn't fill out all the assets in the template"));
      return false;
    }

    this.$(this.options.titleEl).removeClass('error');
    return true;
  },

  /**
   * Callback for toggling the section list from expanded to
   * collapsed.
   *
   * This adjusts the padding of builder element so it has a consistent
   * amount of padding regardless of the height of the section list.
   */
  handleToggleSectionList: function(state) {
    if (_.isUndefined(this._initialPadding)) {
      this._initialPadding = parseInt(this.$el.css('padding-top').replace('px', ''), 10);
    }
    if (state === "closed") {
      this.$el.css('padding-top', 0);
    }
    else {
      this.$el.css('padding-top', this._initialPadding);
    }
  }
});

storybase.builder.views.LastSavedView = Backbone.View.extend({
  tagName: 'div',

  className: 'last-saved container',

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
    this.assets.on("add reset sync remove", this.render, this);
    // When an asset is removed from a section, add it to this view
    this.dispatcher.on("remove:sectionasset", this.addAsset, this);
    this.assets.on("remove", this.handleRemove, this);
  },

  render: function() {
    var assetsJSON = this.assets.toJSON();
    assetsJSON = _.map(assetsJSON, function(assetJSON) {
      // TODO: Better shortened version of asset
      return assetJSON;
    });
    var context = {
      assets: assetsJSON
    };
    this.$el.html(this.template(context));
    this.$('.unused-asset').draggable({
      revert: 'invalid' 
    });
    return this;
  },

  /**
   * Event callback for when assets are removed from a section
   */
  addAsset: function(asset) {
    this.assets.push(asset);
  },

  handleRemove: function() {
    // If the last asset was removed, hide the element
    if (!this.assets.length) {
      this.$el.hide(); 
    }
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

/**
 * View mixin for updating a Story model's attribute and triggering
 * a save to the server.
 */
storybase.builder.views.StoryAttributeSavingMixin = {
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
  }
};

storybase.builder.views.ThumbnailHighlightMixin = {
  highlightClass: 'selected',

  highlightSection: function(section) {
    if (section === this.getSection()) {
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

/**
 * Mixin object that provides a method for doing asynchronous file
 * uploads.
 */
storybase.builder.views.FileUploadMixin = {
  /**
   * Upload a file associated with a model, then refresh the model
   *
   * The heavy lifting is done by jQuery.ajax()
   * 
   * @param object model Model instance that the file will be
   *     associated with on the server side.
   * @param string fileField Name of the file input for the file
   * @param object file File object retrieved from a form's file input
   * @options object Options to configure the AJAX request, especially
   *     callbacks.  progressHandler is the callback for the updating
   *     the upload's progress, beforeSend is the beforeSend callback
   *     for the jQuery AJAX request, and success is the callback for
   *     after the file has been uploaded AND the model's data has
   *     been refreshed from the server.
   *
   * @returns object The jqXHR object returned by the call to 
   *     jQuery.ajax()
   */
  uploadFile: function(model, fileField, file, options) {
    options = _.isUndefined(options) ? {} : options;
    var that = this;
    var url = model.url() + 'upload/';
    var formData = new FormData;
    var settings;
    formData.append(fileField, file);
    settings = {
      type: "POST",
      data: formData,
      cache: false,
      contentType: false,
      processData: false,
      xhr: function() {
        var newXhr = $.ajaxSettings.xhr();
        if (newXhr.upload && options.progressHandler) {
          newXhr.upload.addEventListener('progress', options.progressHandler, false);
        }
        return newXhr;
      },
      beforeSend: function() {
        if (options.beforeSend) {
          options.beforeSend();
        }
      },
      success: function() {
        model.fetch({
          success: function(model, response) {
            if (options.success) {
              options.success(model, response);
            }
          }
        });
      }
    };
    var jqXHR = $.ajax(url, settings);
    return jqXHR;
  }
};


/**
 * Mixin for views that have a navigation subview
 */
storybase.builder.views.NavViewMixin = {
  getNavView: function() {
    return this.navView;
  }
};

/**
 * Next/previous buttons.
 */
storybase.builder.views.SectionNavView = Backbone.View.extend({
  id: 'section-nav',

  className: 'section-nav',

  events: {
    'click .next,.prev': 'handleClick'
  },

  templateSource: $('#section-nav-template').html(),

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    //this._active = 'story-info'; 
    this._active = null;
    this._prev = null;
    this._next = null;

    this.template = Handlebars.compile(this.templateSource);

    this.model.sections.on("remove", this.updatePrevNext, this);
    this.model.sections.on("sync", this.updatePrevNext, this);
    this.dispatcher.on('select:section', this.updateSection, this);
  },

  updatePrevNext: function() {
    if (_.isObject(this._active)) {
      // section is a Section model instance
      index = this.model.sections.indexOf(this._active);
      if (index === 0) {
        this._prev = 'story-info';
      }
      else {
        this._prev = this.model.sections.at(index - 1);
      }

      if (index === this.model.sections.length - 1) {
        this._next = 'call-to-action';
      }
      else {
        this._next = this.model.sections.at(index + 1);
      }
    }
    else {
      // section is a string for the pseudo sections
      if (this._active === 'story-info') {
        // Assume story information view is the first view
        this._prev = null;
        this._next = this.model.sections.at(0);
      }
      else if (this._active === 'call-to-action') {
        this._prev = this.model.sections.last();
        this._next = null;
      }
    }
    console.debug(this._active, this._prev, this._next);

    this.render();
  },

  updateSection: function(section) {
    var index;
    this._active = section;
    this.updatePrevNext();
  },

  /**
   * Get a (pseudo) section's ID.
   */
  getId: function(value) {
    if (_.isObject(value)) {
      // Section is a model
      if (value.isNew()) {
        // It hasn't been saved, so return the client ID
        return value.cid;  
      }
      else {
        // Return the ID
        return value.id;
      }
    }
    else {
      // Section is a pseudo-section ID, just return that string
      return value;
    }
  },

  render: function() {
    var context = {
      prevId: this.getId(this._prev),
      nextId: this.getId(this._next)
    };
    console.debug(context);
    this.$el.html(this.template(context));
    this.delegateEvents();
    return this;
  },

  /**
   * Lookup a (pseudo) section.
   */
  getSection: function(sectionId) {
    var section;
    // If the id is one of the pseudo-section ids, just return
    // the id string
    if (sectionId === 'story-info' || sectionId === 'call-to-action') {
      return sectionId;
    }
    // Next, try to look up the section by the id 
    section = this.model.sections.get(sectionId);
    if (_.isUndefined(section)) {
      // A matching section wasn't found. See if it's a client id
      section = this.model.sections.getByCid(sectionId);
    }
    return section;
  },

  handleClick: function(evt) {
    var sectionId = $(evt.target).attr('id');
    var section = this.getSection(sectionId); 
    evt.preventDefault();
    this.dispatcher.trigger('select:section', section);
  }
});

storybase.builder.views.SectionListView = Backbone.View.extend({
  tagName: 'div',
  
  id: 'section-list',

  className: 'section-list',

  templateSource: $('#section-list-template').html(),

  events: {
    'click .spacer': 'clickSpacer',
    'click #toggle-section-list': 'toggleList',
    'sortupdate': 'handleSort',
    'mousedown .scroll-right': 'scrollRight',
    'mousedown .scroll-left': 'scrollLeft',
    'mouseup': 'stopScroll',
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.navView = this.options.navView;
    this._state = 'opened';
    /**
     * A lookup table of SectionThumbnailView instances by their
     * model's section ids.
     * @type object
     */
    this._thumbnailViews = {};
    /**
     * A list of SectionThumbnailView instances that defines the order
     * of the thumbnails.
     *
     * We have to define this instead of just using the sections collection
     * of the Story model because of the story information and call to 
     * action "pseudo sections".
     * @type array
     */
    this._sortedThumbnailViews = [];
    this._sectionsFetched = false;
    this._thumbnailsAdded = false;
    this._doScroll = false;
    this._thumbnailWidth = 0;

    this.template = Handlebars.compile(this.templateSource);

    this.sectionNavView = new storybase.builder.views.SectionNavView({
      dispatcher: this.dispatcher,
      model: this.model
    });

    this.dispatcher.on("do:remove:section", this.removeSection, this);
    this.dispatcher.on("ready:story", this.addSectionThumbnails, this);

    _.bindAll(this, 'addSectionThumbnail');

    this.$el.html(this.template());
  },

  addSectionThumbnail: function(section, index) {
    var sectionId = section.isNew() ? section.cid : section.id;
    var view = new storybase.builder.views.SectionThumbnailView({
      dispatcher: this.dispatcher,
      model: section
    });
    index = _.isUndefined(index) ? this._sortedThumbnailViews.length - 1 : index + 1; 
    this._sortedThumbnailViews.splice(index, 0, view);
    this._thumbnailViews[sectionId] = view;
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
    this.addStoryInfoThumbnail();
    this.addCallToActionThumbnail();
    this.model.sections.each(this.addSectionThumbnail);
    this._thumbnailsAdded = true;
    if (this.$el.is(':visible')) {
      this.render();
    }
  },

  setWidth: function() {
    var $thumbnails = this.$('.sections').children();
    this._thumbnailWidth = this._thumbnailWidth ||  $thumbnails.eq(0).outerWidth(true);
    var newWidth = ($thumbnails.length * this._thumbnailWidth) + (3 * this._thumbnailWidth);
    this.$('.sections').width(newWidth); 
  },

  render: function() {
    console.info('Rendering the section list');
    var i = 0;
    var numThumbnails;
    var thumbnailView;
    numThumbnails = this._sortedThumbnailViews.length;
    if (numThumbnails) {
      for (i = 0; i < numThumbnails; i++) {
        thumbnailView = this._sortedThumbnailViews[i];
        this.$('.sections').append(thumbnailView.render().el);
      }
      this.$('.sections').sortable({
        items: 'li:not(.pseudo)'
      });
    }
 
    this.setWidth();
    this.$('.sections-clip').css({overflow: 'hidden'});
 
    this.$el.addClass(this._state);
    this.sectionNavView.render();
    if (this._state === 'opened') {
      this.sectionNavView.$el.hide();
    }
    this.$el.append(this.sectionNavView.el);
    if (this.navView) {
      this.$el.append(this.navView.el);
    }
    this.delegateEvents();

    return this;
  },

  getThumbnailView: function(section) {
    // First try looking up the section by section id
    var view = this._thumbnailViews[section.id];
    if (_.isUndefined(view)) {
      // If that fails, look it up by client id
      // This occurs when the section is one copied from the template
      // that hadn't been saved when the thumbnail view lookup object
      // was initialized
      view = this._thumbnailViews[section.cid];
    }
    
    return view; 
  },

  removeThumbnailView: function(view) {
    var index = _.indexOf(this._sortedThumbnailViews, view);
    view.close();
    this._sortedThumbnailViews.splice(index, 1);
    if (_.isUndefined(view.pseudoSectionId)) {
      delete this._thumbnailViews[view.model.id];
    }
    else {
      delete this._thumbnailViews[view.pseudoSectionId];
    }
    this.setWidth();
    this.dispatcher.trigger('remove:thumbnail', view);
  },

  removeSection: function(section) {
    console.debug("Removing section " + section.get("title"));
    var doRemove = false;
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
      doRemove = confirm(gettext("Are you sure you want to delete the section"));
      if (doRemove) {
        section.destroy({
          success: handleSuccess,
          error: handleError
        });
      }
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

  addNewSection: function(index) {
    // TODO: Better method of selecting layout for new section.  This one
    // breaks if you remove all sections
    var section = new storybase.models.Section({
      title: gettext('New Section'),
      layout: this.model.sections.at(0).get('layout'),
      root: true,
      template_section: this.model.sections.at(0).get('template_section')
    });
    var postSave = function(section) {
      var thumbnailView;
      section.off('sync', postSave);
      this.dispatcher.trigger("created:section", section, index);
      thumbnailView = this.addSectionThumbnail(section, index);
      thumbnailView.highlightSection(section);
      this.render();
    };
    postSave = _.bind(postSave, this);
    this.model.sections.add(section, {at: index});
    section.on('sync', postSave);
    this.model.saveSections();
  },

  handleSort: function(evt, ui) {
    console.debug('Handling sort');
    var that = this;
    var sortedIds = this.$('.sections').sortable('toArray');
    this._sortedThumbnailViews = [];
    var addView = _.bind(function(id) {
      this._sortedThumbnailViews.push(this._thumbnailViews[id]);
    }, this);
    this._sortedThumbnailViews.push(this._thumbnailViews['story-info']);
    _.each(sortedIds, addView);
    this._sortedThumbnailViews.push(this._thumbnailViews['call-to-action']);
    this.model.sections.sortByIdList(sortedIds);
    this.model.saveSections();
  },

  startScroll: function(scrollVal) {
    var that = this;
    var $el = this.$('.sections-clip');
    $el.animate({scrollLeft: scrollVal}, 'fast', function() {
      if (that._doScroll) {
        that.startScroll(scrollVal);
      }
    });
  },

  scrollLeft: function(evt) {
    evt.preventDefault();
    this._doScroll = true;
    this.startScroll('-=50');
  },

  scrollRight: function(evt) {
    evt.preventDefault();
    this._doScroll = true;
    this.startScroll('+=50');
  },

  stopScroll: function(evt) {
    evt.preventDefault();
    this._doScroll = false;
  },

  toggleList: function(evt) {
    evt.preventDefault();
    this._state = this._state === 'opened' ? 'closed' : 'opened';
    // TODO: Use the 'blind' easing function to show/hide this
    this.$('.sections-container').toggle();
    this.$el.toggleClass('opened');
    this.$el.toggleClass('closed');
    this.sectionNavView.$el.toggle();
    this.dispatcher.trigger('toggle:sectionlist', this._state);
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


      this.dispatcher.on("select:section", this.highlightSection, this);
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
      this.dispatcher.off("select:section", this.highlightSection, this);
      this.dispatcher.off("remove:thumbnail", this.render, this);
      this.model.off("change", this.render);
      this.model.off("sync", this.render, this);
    },

    getSection: function() {
      return this.model;
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
      this.dispatcher.on("select:section", this.highlightSection, this);
    },

    render: function() {
      var context = {
        title: this.title
      };
      this.$el.html(this.template(context));
      this.delegateEvents();
      return this;
    },

    getSection: function() {
      return this.pseudoSectionId;
    },

    select: function() {
      this.dispatcher.trigger('select:section', this.pseudoSectionId);
    }
}));

storybase.builder.views.PseudoSectionEditView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.RichTextEditorMixin, 
           storybase.builder.views.StoryAttributeSavingMixin, {
    tagName: 'div',

    defaults: {},

    initialize: function() {
      _.defaults(this.options, this.defaults);
      this.dispatcher = this.options.dispatcher;
      this.help = this.options.help;
      this.template = Handlebars.compile(this.templateSource);

      this.dispatcher.on('select:section', this.show, this);
    },

    show: function(id) {
      id = _.isUndefined(id) ? this.pseudoSectionId : id;
      if (id == this.pseudoSectionId) {
        console.debug("Showing editor for pseduo-section " + this.pseudoSectionId);
        this.$el.show();
        // For now, don't automatically show help
        //this.dispatcher.trigger('do:show:help', false, this.help.toJSON()); 
        this.dispatcher.trigger('do:set:help', this.help.toJSON());
      }
      else {
        console.debug("Hiding editor for pseduo-section " + this.pseudoSectionId);
        this.$el.hide();
      }
      return this;
    },

    /**
     * Event handler for when form elements are changed
     */
    change: function(e) {
      var key = $(e.target).attr("name");
      var value = $(e.target).val();
      if ($(e.target).prop('checked')) {
        value = true;
      }
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
    titleEl: '.story-title',
    bylineEl: '.byline',
    summaryEl: 'textarea[name="summary"]' 
  },

  render: function() {
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
      tooltip: gettext('Click to edit title'),
      onblur: 'submit'
    });
    this.$(this.options.bylineEl).editable(editableCallback, {
      placeholder: gettext('Click to edit byline'),
      tooltip: gettext('Click to edit byline'),
      onblur: 'submit'
    });
    this.delegateEvents(); 
    return this;
  }
});

/**
 * View for editing story information in the connected story builder.
 *
 * This view should be attached inside the section edit view
 *
 */
storybase.builder.views.InlineStoryInfoEditView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.StoryAttributeSavingMixin, {
    className: 'edit-story-info-inline',

    templateSource: $('#story-info-edit-inline-template').html(),

    defaults: {
      titleEl: '.story-title',
      bylineEl: '.byline'
    },

    initialize: function() {
      _.defaults(this.options, this.defaults);
      this.template = Handlebars.compile(this.templateSource);
      this.dispatcher = this.options.dispatcher;
    },

    render: function() {
      var that = this;
      var editableCallback = function(value, settings) {
        that.saveAttr($(this).data("input-name"), value);
        return value;
      };
      var context = this.model.toJSON();
      context.prompt = this.options.prompt;
      this.$el.html(this.template(context));
        
      this.$(this.options.titleEl).editable(editableCallback, {
        placeholder: gettext('Click to edit title'),
        tooltip: gettext('Click to edit title'),
        onblur: 'submit'
      });
      this.$(this.options.bylineEl).editable(editableCallback, {
        placeholder: gettext('Click to edit byline'),
        tooltip: gettext('Click to edit byline'),
        onblur: 'submit'
      });
      this.delegateEvents(); 
      return this;
    }
  })
);

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
    callToActionEl: 'textarea[name="call_to_action"]',
    connectedEl: 'input[name="allow_connected"]',
    connectedPromptEl: 'textarea[name="connected_prompt"]'
  },

  templateSource: $('#story-call-to-action-edit-template').html(),

  events: function() {
    var events = {};
    events['change ' + this.options.callToActionEl] = 'change';
    events['change ' + this.options.connectedEl] = 'changeConnectedEl';
    events['change ' + this.options.connectedPromptEl] = 'change';
    return events;
  },

  changeConnectedEl: function(evt) {
    this.change(evt);
    console.debug('In changeConnectedEl');
    if ($(evt.target).prop('checked')) {
      this.$(this.options.connectedPromptEl).show(); 
    }
    else {
      this.$(this.options.connectedPromptEl).hide(); 
    }
  },

  render: function() {
    var that = this;
    var handleChange = function () {
      // Trigger the change event on the underlying element 
      that.$(that.options.callToActionEl).trigger('change');
    };
    this.$el.html(this.template(this.model.toJSON()));
    // Add the toolbar element for the wysihtml5 editor
    // Initialize wysihmtl5 editor
    this.callEditor = this.getEditor(
      this.$(this.options.callToActionEl)[0],
      {
        change: handleChange
      }
    );
    this.delegateEvents();
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
    containerEl: '.storybase-container-placeholder',
    titleEl: '.section-title',
    storyTitleEl: '.story-title'
  },

  events: {
    "change select.layout": 'change'
  },

  initialize: function() {
    _.defaults(this.options, this.defaults);
    this.containerTemplates = this.options.containerTemplates;
    this.dispatcher = this.options.dispatcher;
    this.story = this.options.story;
    this.layouts = this.options.layouts;
    this.defaultHelp = this.options.defaultHelp;
    this.templateSource = this.options.templateSource || this.templateSource;
    this.templateSection = this.options.templateSection;
    this.template = Handlebars.compile(this.templateSource);
    this.assets = this.model.assets;
    this._unsavedAssets = [];
    this._doConditionalRender = false;
    this._firstSave = this.model.isNew();
    
    // Edit the story information within the section edit view
    // This is mostly used in the connected story builder
    if (this.options.showStoryInfoInline) {
      this.storyInfoEditView = new storybase.builder.views.InlineStoryInfoEditView({
        dispatcher: this.dispatcher,
        model: this.story,
        prompt: this.options.prompt
      });
    }

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
    console.debug('Rendering asset views');
    var that = this;
    var containerTemplate;
    this.$(this.options.containerEl).each(function(index, el) {
      var options = {
        el: el,
        container: $(el).attr('id'),
        dispatcher: that.dispatcher,
        section: that.model, 
        story: that.story,
        assetTypes: that.options.assetTypes
      };
      if (that.assets.length) {
        // If there are assets, bind them to the view with the appropriate
        // container
        options.model = that.assets.where({container: $(el).attr('id')})[0];
      }
      if (that.templateSection && that.containerTemplates.length) {
        containerTemplate = that.containerTemplates.where({
          section: that.templateSection.id,
          container: $(el).attr('id')
        })[0];
        if (containerTemplate) {
          options.suggestedType = containerTemplate.get('asset_type');
          options.canChangeAssetType = containerTemplate.get('can_change_asset_type');
          options.help = containerTemplate.get('help');
        }
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
    context.showSectionTitles = this.options.showSectionTitles;
    context.showLayoutSelection = this.options.showLayoutSelection;
    this.$el.html(this.template(context));
    if (this.storyInfoEditView) {
      this.$el.prepend(this.storyInfoEditView.render().el);
    }
    if (this.model.isNew()) {
      this.renderAssetViews();
    }
    else {
      this.assets.fetch();
    }
    if (this.options.showSectionTitles) {
      this.$(this.options.titleEl).editable(editableCallback, {
        placeholder: gettext('Click to edit title'),
        tooltip: gettext('Click to edit title'),
        onblur: 'submit'
      });
    }
    return this;
  },

  show: function(section) {
    section = _.isUndefined(section) ? this.model : section;
    var help = this.model.get('help') || this.defaultHelp.toJSON();
    if (section == this.model) {
      console.debug('showing section ' + section.get('title'));
      this.$el.show();
      // For now, don't show help automatically
      //this.dispatcher.trigger('do:show:help', false, help); 
      this.dispatcher.trigger('do:set:help', help);
    }
    else {
      console.debug('hiding section ' + this.model.get('title'));
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
    this.assets.each(function(asset) {
      this.removeAsset(this.model, asset);
    }, this);
  },

  /**
   * Event handler for when assets are added to the section
   */
  addAsset: function(section, asset, container) {
    if (section == this.model) {
      // Artifically set the container attribute of the asset.
      // For assets retrieved from the server, this is handled by
      // SectionAssets.parse()
      asset.set('container', container);
      this.assets.add(asset);
      this.story.assets.add(asset);
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
   * Callback for when an asset is removed from the section
   */
  removeAsset: function(section, asset) {
    if (section == this.model) {
      var that = this;
      var sectionAsset = this.getSectionAsset(asset);
      sectionAsset.id = asset.id;
      sectionAsset.destroy({
        success: function(model, response) {
          that.assets.remove(asset);
          that.dispatcher.trigger("remove:sectionasset", asset);
          that.dispatcher.trigger("alert", "info", "You removed an asset, but it's not gone forever. You can re-add it to a section from the asset list");
        },
        error: function(model, response) {
          that.dispatcher.trigger("error", "Error removing asset from section");
        }
      });
    }
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
    console.debug('Saving section asset');
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

  /**
   * Callback for the 'destroy' event on the view's model.
   */
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
    // Remove the section from the collection of all sections
    this.collection.splice(_.indexOf(this.collection, this), 1);
    // Inform the user that the section has been deleted
    this.dispatcher.trigger('alert', 'success', gettext('The section  "' + this.model.get('title') + '" has been deleted'));
    this.close();
  },

  getContainerIds: function() {
    var ids = [];
    this.$(this.options.containerEl).each(function(index, el) {
      ids.push($(el).attr('id'));
    });
    return ids;
  },

  allAssetsDefined: function() {
    var containerIds = this.getContainerIds();
    return _.reduce(this.getContainerIds(), function(memo, id) {
      var matching;
      if (memo === false) {
        return false;
      }
      else { 
        matching = this.assets.where({container: id});
        return matching.length > 0;
      }
    }, true, this);
  }
});

storybase.builder.views.SectionAssetEditView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.FileUploadMixin, 
           storybase.builder.views.RichTextEditorMixin, {
    tagName: 'div',

    className: 'edit-section-asset',

    defaults: {
      wrapperEl: '.wrapper',
      helpPopupEl: '.asset-help-container'
    },

    templateSource: function() {
      var state = this.getState(); 
      if (state === 'display') {
        return $('#section-asset-display-template').html();
      }
      else if (state === 'edit') {
        return $('#section-asset-edit-template').html();
      }
      else if (state === 'upload') {
        return $('#asset-uploadprogress-template').html();
      }
      else {
        // state === 'select'
        return $('#section-asset-select-type-template').html();
      }
    },

    helpTemplateSource: $('#section-asset-help-template').html(),

    events: {
      "click .asset-type": "selectType", 
      "click .remove": "remove",
      "click .edit": "edit",
      "mouseenter .help": "showHelp",
      "mouseleave .help": "hideHelp",
      'click input[type="reset"]': "cancel",
      'submit form.bbf-form': 'processForm',
      'drop': 'handleDrop'
    },

    states: ['select', 'display', 'edit'],

    initialize: function() {
      console.debug("Initializing new section asset edit view");
      _.defaults(this.options, this.defaults);
      var modelOptions = {};
      this.container = this.options.container;
      this.dispatcher = this.options.dispatcher;
      this.assetTypes = this.options.assetTypes;
      this.section = this.options.section;
      this.story = this.options.story;
      this.helpTemplate = Handlebars.compile(this.helpTemplateSource); 
      if (_.isUndefined(this.model)) {
        if (this.options.suggestedType) {
          modelOptions.type = this.options.suggestedType;
        }
        this.model = new storybase.models.Asset(modelOptions);
      }
      _.bindAll(this, 'uploadFile', 'handleUploadProgress', 'editCaption'); 
      this.bindModelEvents();
      this.initializeForm();
      this.setInitialState();
    },

    bindModelEvents: function() {
      this.model.on("change", this.initializeForm, this);
    },

    unbindModelEvents: function() {
      this.model.off("change", this.initializeForm, this);
    },

    /**
     * Cleanup the view.
     */
    close: function() {
      this.remove();
      this.undelegateEvents();
      this.unbind();
      this.unbindModelEvents();
    },

    /** 
     * Update the view's form labels based on the asset type.
     */
    updateFormLabels: function() {
      var type = this.model.get('type');
      var num_elements = _.size(_.pick(this.form.schema, 'image', 'body', 'url')); 
      var prefix = num_elements > 1 ? gettext("or") + ", " : "";
      if (this.form.schema.url) {
        this.form.schema.url.title = capfirst(gettext("enter") + " " + type + " " + gettext("URL"));
      }
      if (this.form.schema.image) {
        this.form.schema.image.title = capfirst(prefix + gettext("select an image from your own computer to be included in your story."));
      }
      if (this.form.schema.body) {
        if (type === 'text') {
          this.form.schema.body.template = 'noLabelField';
        }
        else if (type === 'quotation') {
          this.form.schema.body.title = capfirst(prefix + gettext("enter the quotation text"));
        }
        else {
          this.form.schema.body.title = capfirst(prefix + gettext("paste the embed code for the") + " " + type);
        }
      }
    },

    /**
     * Set the view's form property based on the current state of the model.
     */
    initializeForm: function() {
      console.debug("Initializing asset edit form");
      this.form = new Backbone.Form({
        model: this.model
      });
      this.updateFormLabels(); 
      this.form.render();
    },

    setClass: function() {
      var activeState = this.getState();
      _.each(this.states, function(state) {
        if (state === activeState) {
          this.$el.addClass(state);
        }
        else {
          this.$el.removeClass(state);
        }
      }, this);
    },

    /**
     * Get a list of asset types and their labels, filtering out the
     * default type.
     */
    getAssetTypes: function() {
      var type = this.options.suggestedType;
      if (type) {
        return _.filter(this.assetTypes, function(at) {
          return at.type !== type;
        });
      }
      else {
        return this.assetTypes;
      }
    },

    getDefaultAssetType: function() {
      var type = this.options.suggestedType;
      if (type) {
        return _.filter(this.assetTypes, function(at) {
          return at.type === type;
        })[0];
      }
      else {
        return null;
      }
    },

    render: function() {
      var context = {};
      var editableCallback = function(value, settings) {
        that.saveAttr($(this).data("input-name"), value);
        return value;
      };
      var state = this.getState();
      var $wrapperEl;
      this.template = Handlebars.compile(this.templateSource());
      if (state === 'select') {
        if (this.options.canChangeAssetType || _.isUndefined(this.options.canChangeAssetType)) {
          context.assetTypes = this.getAssetTypes();
        }
        context.defaultType = this.getDefaultAssetType(); 
        context.help = this.options.help;
      }
      else if (state === 'display') {
        context.model = this.model.toJSON()
      }
      this.$el.html(this.template(context));
      $wrapperEl = this.$(this.options.wrapperEl);
      this.setClass();
      if (state == 'select') {
        // The accept option needs to match the class on the items in
        // the UnusedAssetView list
        $wrapperEl.droppable({ accept: ".unused-asset" });
      }
      if (state == 'display') {
        if (!this.$('.caption').length && this.model.formFieldVisible('caption', this.model.get('type'))) {
          $wrapperEl.append($('<div class="caption"></div>'));
        }
        this.$('.caption').editable(this.editCaption, {
          type: 'textarea',
          cancel: gettext("Cancel"),
          submit: gettext("Save"),
          tooltip: gettext("Click to edit"),
          placeholder: gettext("Click to edit caption")
        });
      }
      if (state === 'edit') {
        this.form.render().$el.append('<input type="reset" value="' + gettext("Cancel") + '" />').append('<input type="submit" value="' + gettext("Save Changes") + '" />');
        if (_.has(this.form.fields, 'body') && this.model.get('type') == 'text') {
          this.bodyEditor = this.getEditor(
            this.form.fields.body.editor.el
          );
          // HACK: Get rid of the default event handlers
          // They seem to prevent event bubbling, e.g. the editor's blur event
          // handler gets callled and the "Save"/"Cancel" buttons' click 
          // events never get called.  I think this is okay for now, since the
          // toolbar showing/hiding doesn't make as much sense when editing the
          // asset views.
          this.bodyEditor.stopObserving('blur');
          this.bodyEditor.stopObserving('load');
        }
        $wrapperEl.append(this.form.el);
      }

      return this;
    },

    /**
     * Callback for Jeditable plugin applied to caption.
     */
    editCaption: function(value, settings) {
      // Call this.saveModel instead of this.model.save() mostly
      // because calling this.model.save() without a callback causes
      // the "sync" event to bubble up to the collection, which we don't
      // want.
      this.saveModel({caption: value});
      return value;
    },

    setInitialState: function() {
      if (!this.model.isNew()) {
        this._state = 'display';
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

    saveModel: function(attributes, options) {
      console.debug("Saving asset");
      options = _.isUndefined(options) ? {} : options;
      var that = this;
      // Save the model's original new state to decide
      // whether to send a signal later
      var isNew = this.model.isNew();
      this.model.save(attributes, {
        success: function(model) {
          that.setState('display');
          that.render();
          if (isNew) {
            // Model was new before saving
            that.dispatcher.trigger("do:add:sectionasset", that.section,
              that.model, that.container
            );
          }
          if (options.success) {
            options.success(model);
          }
        },
        error: function(model) {
          that.dispatcher.trigger('error', 'error saving the asset');
        }
      });
    },

    /**
     * Event callback for updating the progress of an upload.
     */
    handleUploadProgress: function(evt) {
      if (evt.lengthComputable) {
        var percentage = Math.round((evt.loaded * 100) / evt.total);
        this.$('.uploadprogress').text(gettext('Uploading') + ': ' + percentage + '%');
      }
    },

    /**
     * Event handler for submitting form
     */
    processForm: function(e) {
      e.preventDefault();
      console.info("Editing asset");
      var errors = this.form.validate();
      var data;
      var file;
      var options = {};
      var that = this;
      if (!errors) {
        var data = this.form.getValue();
        if (data.image) {
          file = data.image;
          // Set a callback for saving the model that will upload the
          // image.
          options.success = function(model) {
            that.uploadFile(model, 'image', file, {
              progressHandler: that.handleUploadProgress,
              beforeSend: function() {
                that.setState('upload');
                that.render();
              },
              success: function(model, response) {
                that.setState('display');
                that.render();
              }
            });
          };
        }

        // Delete the image property.  We've either retrieved it for
        // upload or it was empty (meaning we don't want to change the
        // image.
        delete data.image;
        this.saveModel(data, options);
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
      // This view should no longer listen to events on this model
      this.unbindModelEvents();
      this.dispatcher.trigger('do:remove:sectionasset', this.section, this.model);
      this.model = new storybase.models.Asset();
      // Listen to events on the new model
      this.bindModelEvents();
      this.setState('select').render();
    },

    assetTypeHelp: {
      image: gettext('Click on "Add your image," then enter a URL or upload an image from your computer. If you’d like to add a different type of asset, click below.'),
      text: gettext('Click on “Add your text,” and start typing. If you’d like to add a different type of asset, click below.')
      // TODO: Add help text for other items
    },

    getAssetTypeHelp: function(type) {
      var help = this.assetTypeHelp[type]; 
      if (_.isUndefined(help)) {
        help = "TODO: Add help text!";
      }
      return help;
    },

    /**
     * Show a help popup.
     */
    // TODO: Generalize this to be used in other cases. 
    showHelp: function(evt) {
      var targetWidth = $(evt.target).outerWidth();
      var windowWidth = $(window).width();
      var windowLeft = $(window).scrollLeft();
      var offset = $(evt.target).offset();
      var popupClass = this.options.helpPopupEl.replace('.', '');
      // Shift the popup this far
      var popupOffsetX = 8;
      var popupTop = offset.top;
      // Default to positiioning the popup to the right of the
      // clicked element
      var popupLeft = offset.left + targetWidth + popupOffsetX;
      var popupWidth;
      var $popupEl;
      var context = {
        typeHelp: this.getAssetTypeHelp(this.options.suggestedType)
      };
      var template = this.helpTemplate;

      _.defaults(context, this.options.help);
      $popupEl = $('<div class="' + popupClass + '">' + template(context) + '</div>').appendTo('body').hide();
      popupWidth = $popupEl.outerWidth();

      // Check if the popup will fall off the right of the screen
      if ((popupLeft + popupWidth) - windowLeft > windowWidth) {
        // The popup should go to the left of the element
        popupLeft = offset.left - popupOffsetX - popupWidth;
      }

      $popupEl.css({
        'position': 'absolute',
        'top': popupTop+'px',
        'left': popupLeft+'px'
      });
      $popupEl.show();
    },

    hideHelp: function(evt) {
      var popupEl = this.options.helpPopupEl;
      $(popupEl).hide();
      $(popupEl).remove();
    },

    handleDrop: function(evt, ui) {
      console.debug("Asset dropped");
      var id = ui.draggable.data('asset-id');
      if (id) {
        this.model = this.story.unusedAssets.get(id);
        this.story.unusedAssets.remove(this.model);
        if (!this.story.unusedAssets.length) {
          this.dispatcher.trigger('has:assetlist', false);
        }
        this.setState('display');
        this.dispatcher.trigger("do:add:sectionasset", this.section, this.model, this.container);
        this.render();
      }
    }
  })
);

storybase.builder.views.DataView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.NavViewMixin, storybase.builder.views.FileUploadMixin, {
    className: 'container',

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

      this.navView = new storybase.builder.views.WorkflowNavView({
        model: this.model,
        dispatcher: this.dispatcher,
        items: [
          {
            id: 'workflow-nav-build-back',
            text: gettext("Continue Writing Story"),
            path: ''
          },
          {
            id: 'workflow-nav-tag-fwd',
            text: gettext("Tag"),
            path: 'tag/'
          }
        ]
      });

      this.form = new Backbone.Form({
        schema: this.getFormSchema() 
      }); 
    },

    /**
     * Get the Backbone Forms schema for the data set addition form
     */
    getFormSchema: function() {
      // Start with the schema defined in the model
      var schema = storybase.models.DataSet.prototype.schema();
      // Update some labels
      schema.title.title = gettext("Data set name");
      schema.source.title = gettext("Data source");
      schema.url.title = gettext("Link to a data set");
      schema.file.title = gettext("Or, upload a data file from your computer");
      return schema;
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
      if (!this._collectionFetched) {
        this.fetchCollection();
      }
      else {
        console.info('Rendering data view');
        var context = {
          datasets: this.collection.toJSON()
        };
        this.$el.html(this.template(context));
        this.$('.add-dataset').before(this.form.render().$el.append('<input class="cancel" type="reset" value="Cancel" />').append('<input type="submit" value="Save" />').hide());
        this.navView.render();
        this.delegateEvents();
      }
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
        this.addDataSet(formData);
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
      var file = null;
      if (attrs.file) {
        file = attrs.file;
        delete attrs.file;
      }
      this.collection.create(attrs, {
        success: function(model, response) {
          that.trigger('save:dataset', model);
          if (file) {
            that.uploadFile(model, 'file', file, {
              success: function(model, response) {
                that.dispatcher.trigger('alert', 'success', "Data set added");
                that.render();
              }
            });
          }
          else {
            that.dispatcher.trigger('alert', 'success', "Data set added");
            that.render();
          }
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
  })
);

storybase.builder.views.ReviewView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.NavViewMixin, {
    className: 'container',

    templateSource: $('#review-template').html(),

    events: {
      'click .preview': 'previewStory'
    },

    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      this.template = Handlebars.compile(this.templateSource);
      this.previewed = false;
      // Need to bind validate to this before it's passed as a callback to
      // the WorkflowNavView instance
      _.bindAll(this, 'hasPreviewed');
      this.navView = new storybase.builder.views.WorkflowNavView({
        model: this.model,
        dispatcher: this.dispatcher,
        items: [
          {
            id: 'workflow-nav-tag-back',
            text: gettext("Back to Tag"),
            path: 'tag/'
          },
          {
            id: 'workflow-nav-publish-fwd',
            text: gettext("Publish My Story"),
            path: 'publish/',
            enabled: this.hasPreviewed,
            validate: this.hasPreviewed
          }
        ]
      });
      if (_.isUndefined(this.model)) {
        this.dispatcher.on("ready:story", this.setStory, this);
      }
    },

    setStory: function(story) {
      this.model = story;
    },

    render: function() {
      console.info('Rendering review view');
      var context = {};
      this.$el.html(this.template(context));
      this.navView.render();
      this.delegateEvents();
      return this;
    },

    previewStory: function(evt) {
      evt.preventDefault();
      var url = '/stories/' + this.model.id + '/viewer/';
      this.previewed = true;
      // Re-render the nav view to reflect the newly enabled button
      this.navView.render();
      window.open(url);
    },

    hasPreviewed: function() {
      return this.previewed;
    }
  })
);

storybase.builder.views.LegalView = Backbone.View.extend({
  id: 'share-legal',

  templateSource: $('#share-legal-template').html(),

  events: {
    'change input[name=license]': 'changeLicenseAgreement',
    'submit form': 'processForm'
  },

  // Schema for form
  schema: function (){
    // Custom validator for checkboxes.  For whatever reason, 'required'
    // didn't work
    var isChecked = function(value, formValues) {
      var err = {
        type: 'checked',
        message: gettext("You must check this checkbox")
      };
      if (!value.length) {
        return err;
      }
    };
    return {
      permission: { 
        type: 'Checkboxes',
        title: '',
        options: Handlebars.compile($('#share-permission-field-template').html())(),
        validators: [isChecked]
      },
      license: {
        type: 'Checkboxes',
        title: '',
        options: Handlebars.compile($('#share-license-field-template').html())(),
        validators: [isChecked]
      },
      'cc-allow-commercial': {
        type: 'Radio',
        title: '',
        options: Handlebars.compile($('#share-cc-allow-commercial-template').html())(),
        validators: ['required']
      },
      'cc-allow-modification': {
        type: 'Radio',
        title: '',
        options: Handlebars.compile($('#share-cc-allow-modification-template').html())(),
        validators: ['required']
      }
    };
  },

  initialize: function() {
    var licenseFormVals = this.getLicense();
    var formValues = {
      permission: this.hasPermission,
      license: this.agreedLicense,
      'cc-allow-commercial': licenseFormVals.allowCommercial,
      'cc-allow-modification': licenseFormVals.allowModification
    };
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
    this.hasPermission = this.model && this.model.get('status') === 'published';
    this.agreedLicense = this.model && this.model.get('status') === 'published';
    this.form = new Backbone.Form({
      schema: this.schema(),
      data: formValues
    });
    if (_.isUndefined(this.model)) {
      this.dispatcher.on("ready:story", this.setStory, this);
    }
  },

  setStory: function(story) {
    this.model = story;
  },

  getLicense: function() {
    var ccLicenses = {
      'CC BY': {
        allowCommercial: 'yes',
        allowModification: 'yes'
      },
      'CC BY-SA': {
        allowCommercial: 'yes',
        allowModification: 'share-alike'
      },
      'CC BY-ND': {
        allowCommercial: 'yes',
        allowModification: 'no'
      },
      'CC BY-NC': {
        allowCommercial: 'no',
        allowModification: 'yes'
      },
      'CC BY-NC-SA': {
        allowCommercial: 'no',
        allowModification: 'share-alike'
      },
      'CC BY-NC-ND': {
        allowCommercial: 'no',
        allowModification: 'no'
      }
    };
    var license = this.model ? this.model.get('license') : false;
    if (license) {
      return ccLicenses[license];
    }
    else {
      return ccLicenses['CC BY'];
    }
  },

  setLicense: function(allowCommercial, allowModification) {
    var ccLicenses = {
      'yes': {
        'yes': 'CC BY',
        'share-alike': 'CC BY-SA', 
        'no': 'CC BY-ND'
      },
      'no': {
        'yes': 'CC BY-NC',
        'share-alike': 'CC BY-NC-SA',
        'no': 'CC BY-NC-ND'
      }
    }
    this.model.set('license', ccLicenses[allowCommercial][allowModification]);
    this.model.save();
  },

  validate: function() {
    var formValues = this.form.getValue();
    var errors = this.form.validate();
    if (!errors) {
      this.setLicense(formValues['cc-allow-commercial'],
        formValues['cc-allow-modification']
      );
      this.hasPermission = true;
      this.agreedLicense = true;
      return true;
    }
    else {
      return false;
    }
  },

  processForm: function(evt) {
    evt.preventDefault();
    if (this.validate()) {
      console.debug("Form Valide");
      this.dispatcher.trigger("accept:legal");
    }
  },

  setRadioEnabled: function() {
    this.form.fields['cc-allow-commercial'].$('input').prop('disabled', !this.agreedLicense);
    this.form.fields['cc-allow-modification'].$('input').prop('disabled', !this.agreedLicense);
  },

  /**
   * Workaround for limitations of form initial value setting.
   */
  updateFormDefaults: function() {
    // HACK: Work around weird setValue implementation for checkbox
    // type.  Maybe make a custom editor that does it right.
    this.form.fields.permission.editor.$('input[type=checkbox]').prop('checked', this.hasPermission);
    this.form.fields.license.$('input[type=checkbox]').prop('checked', this.agreedLicense);
    this.setRadioEnabled();
  },

  render: function() {
    this.$el.html(this.template());
    this.form.render().$el.append('<input type="submit" value="' + gettext("Agree") + '" />');
    this.$el.append(this.form.el);
    this.updateFormDefaults();
    this.delegateEvents();

    return this;
  },

  changeLicenseAgreement: function(evt) {
    this.agreedLicense = $(evt.target).prop('checked');
    this.setRadioEnabled();
  },

  acceptedLegalAgreement: function() {
    return this.agreedLicense && this.hasPermission;
  }
});

storybase.builder.views.TaxonomyView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.NavViewMixin, {
    id: 'share-taxonomy',

    className: 'container',

    templateSource: $('#share-taxonomy-template').html(),

    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      this.template = Handlebars.compile(this.templateSource);
      this.navView = new storybase.builder.views.WorkflowNavView({
        model: this.model,
        dispatcher: this.dispatcher,
        items: [
          {
            id: 'workflow-nav-data-back',
            text: gettext("Back to Add Data"),
            path: 'data/'
          },
          {
            id: 'workflow-nav-review-fwd',
            text: gettext("Review"),
            path: 'review/'
          }
        ]
      });
      this.addLocationView = new storybase.builder.views.AddLocationView({
        model: this.model,
        dispatcher: this.dispatcher
      });
      this.tagView = new storybase.builder.views.TagView({
        model: this.model,
        dispatcher: this.dispatcher
      });

      if (this.model) {
        this.initializeForm();
      }
      else {
        this.dispatcher.on('ready:story', this.setStory, this);
      }
    },

    initializeForm: function() {
      // Convert the JSON into the format for Backbone Forms
      var topicsOptions = this.getFormOptions(this.options.topics);
      var placesOptions = this.getFormOptions(this.options.places);
      var organizationsOptions = this.getFormOptions(this.options.organizations, 'organization_id');
      var projectsOptions = this.getFormOptions(this.options.projects, 'project_id');
      // Default editor attributes for the Backbone Form
      var editorAttrs = {
        multiple: "",
        style: "width: 300px"
      };
      // Official taxonomies
      var schema = {
        topics: { 
          type: 'Select', 
          options: topicsOptions, 
          editorAttrs: _.defaults({placeholder: gettext("Click to select topics")}, editorAttrs)
        },
        places: { 
          type: 'Select', 
          options: placesOptions, 
          editorAttrs: _.defaults({placeholder: gettext("Click to select places")}, editorAttrs)
        },
        organizations: {
          type: 'Select',
          options: organizationsOptions,
          editorAttrs: _.defaults({placeholder: gettext("Click to select organizations")}, editorAttrs)
        },
        projects: {
          type: 'Select',
          options: projectsOptions,
          editorAttrs: _.defaults({placeholder: gettext("Click to select projects")}, editorAttrs)
        }
      };
      if (!organizationsOptions.length) {
        delete schema.organizations;
      }
      if (!projectsOptions.length) {
        delete schema.projects;
      }
      this.officialForm = new Backbone.Form({
        schema: schema
      });
      this.officialForm.on('topics:change', this.changeTopics, this);
      this.officialForm.on('places:change', this.changePlaces, this);
      this.officialForm.on('organizations:change', this.changeOrganizations, this);
      this.officialForm.on('projects:change', this.changeProjects, this);
    },

    setStory: function(story) {
      this.model = story;
      this.initializeForm();
    },

    /**
     * Map the options from JSON provided from Django to the format needed
     * by Backbone Forms for creating an HTML select element.
     *
     * See https://github.com/powmedia/backbone-forms#editor-select
     *
     * @param {Array} rawOptions Array of objects representing option
     *     with attributes for keys and values.
     * @param {String} [valAttr="id"] Name of property of the objects in
     *     rawOptions that identifies the value of the option element.
     * @param {String} [labelAttr="name"] Name of property of the objects in
     *     rawOptions that identifies the text of the option element.
     * @returns {Array} Array of objects with val and label properties.
     */
    getFormOptions: function(rawOptions, valAttr, labelAttr) {
      // Set defaults for attributes for creating select options
      valAttr = valAttr ? valAttr : 'id';
      labelAttr = labelAttr ? labelAttr: 'name';
      return _.map(rawOptions, function(value) {
        return {
          val: value[valAttr], 
          label: value[labelAttr],
        };
      });
    },

    replaceRelated: function(url, data) {
      data = data ? data : [];
      $.ajax(url, {
        type: "PUT", 
        data: JSON.stringify(data),
        contentType: "application/json",
        processData: false
      });
    },

    changeTopics: function(form, editor) {
      var url = this.model.url() + 'topics/'; 
      this.replaceRelated(url, editor.getValue());
    },

    changePlaces: function(form, editor) {
      var url = this.model.url() + 'places/'; 
      this.replaceRelated(url, editor.getValue());
    },

    changeOrganizations: function(form, editor) {
      var url = this.model.url() + 'organizations/'; 
      this.replaceRelated(url, editor.getValue());
    },

    changeProjects: function(form, editor) {
      var url = this.model.url() + 'projects/'; 
      this.replaceRelated(url, editor.getValue());
    },

    render: function() {
      var initialValues = {
        'topics': _.pluck(this.model.get('topics'), 'id'),
        'places': _.pluck(this.model.get('places'), 'id'),
      }
      this.$el.html(this.template());
      this.$('#taxonomy').append(this.officialForm.render().el);
      if (this.officialForm.fields.organizations) {
        initialValues.organizations = _.pluck(this.model.get('organizations'), 'id');
      }
      if (this.officialForm.fields.projects) {
        initialValues.projects = _.pluck(this.model.get('projects'), 'id');
      }
      this.officialForm.setValue(initialValues);
      
      // TODO: Custom editor that automatically does this?
      this.officialForm.fields.topics.editor.$el.select2({width: 'resolve'});
      this.officialForm.fields.places.editor.$el.select2({width: 'resolve'});
      if (this.officialForm.fields.organizations) {
        this.officialForm.fields.organizations.editor.$el.select2({width: 'resolve'});
      }
      if (this.officialForm.fields.projects) {
        this.officialForm.fields.projects.editor.$el.select2({width: 'resolve'});
      }
      this.$el.append(this.tagView.render().el);
      this.$el.append(this.addLocationView.render().el);
      this.navView.render();

      return this;
    },

    onShow: function() {
      this.addLocationView.onShow();
    }
  })
);

storybase.builder.views.AddLocationView = Backbone.View.extend({
  id: 'add-location',

  mapId: 'map',

  events: {
    'click #search-address': 'searchAddress',
    'click .delete': 'deleteLocation',
    'submit': 'addLocation'
  },

  templateSource: $('#add-location-template').html(),

  locationTemplateSource: $('#add-location-location-item-template').html(),

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
    this.locationTemplate = Handlebars.compile(this.locationTemplateSource);
    this.initialCenter = new L.LatLng(storybase.globals.MAP_CENTER[0],
                                      storybase.globals.MAP_CENTER[1]);
    this.initialZoom = storybase.globals.MAP_ZOOM_LEVEL;
    this.collection = new storybase.collections.Locations([], {story: this.model});
    this.pointZoom = storybase.globals.MAP_POINT_ZOOM_LEVEL;
    this.latLng = null;
    this._collectionFetched = false;
    this.collection.on("reset", this.renderLocationList, this);
    this.collection.on("add", this.renderLocationList, this);
    this.collection.on("remove", this.renderLocationList, this);
  },

  render: function() {
    console.debug("Rendering add location view");
    if (!this._collectionFetched) {
      this.collection.fetch();
    }
    this.$el.html(this.template());
    this.renderLocationList();
    // Don't show the address name input until an address has been found
    this.$('#address-name-container').hide();
    // Disable the submission button until an address has been found
    this.$('#do-add-location').prop('disabled', true);
    this.delegateEvents();
    return this;
  },

  onShow: function() {
    this.map = new L.Map(this.$('#map')[0], {
    });
    this.map.setView(this.initialCenter, this.initialZoom);
    var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        osmAttrib = 'Map data &copy; 2012 OpenStreetMap contributors',
        osm = new L.TileLayer(osmUrl, {maxZoom: 18, attribution: osmAttrib});
    this.map.addLayer(osm);
    this.markers = new L.LayerGroup();
    this.map.addLayer(this.markers);
  },

  renderLocationList: function(collection) {
    console.debug("In renderLocationList()");
    this.$('#locations').empty(); 
    this.collection.each(function(loc) {
      this.$('#locations').append($(this.locationTemplate(loc.toJSON())));
    }, this);
  },

  searchAddress: function(evt) {
    evt.preventDefault();
    console.debug("Entering searchAddress");
    var address = this.$("#address").val();
    var that = this;
    this.rawAddress = '';
    // Don't show the address name input until an address has been found
    this.$('#address-name-container').hide();
    // Disable the submission button until an address has been found
    this.$('#do-add-location').prop('disabled', true);
    this.$('#found-address').html(gettext("Searching ..."));
    this.$('#address-name').val(null);
    this.markers.clearLayers();
    geocode(address, {
      success: function(latLng, place) {
        that.geocodeSuccess(latLng, place, address);
      },
      failure: function(address) {
        that.$('#found-address').val(gettext("No address found"));
      }
    });
  },

  /**
   * Callback for a successful response from the geocoder.
   */
  geocodeSuccess: function(latLng, place, queryAddress) {
    var center = new L.LatLng(latLng.lat, latLng.lng);
    var marker = new L.Marker(center);
    this.rawAddress = place || queryAddress || "";
    this.$('#found-address').html(this.rawAddress);
    this.$('#address-name-container').show();
    this.$('#do-add-location').prop('disabled', false);
    this.markers.addLayer(marker);
    this.map.setView(marker.getLatLng(), this.pointZoom, true);
    this.latLng = latLng; 
  },

  addLocation: function(evt) {
    evt.preventDefault();
    console.debug('Adding location');
    var name = this.$('#address-name').val();
    // Make sure we found a point
    if (this.latLng) {
      this.collection.create({
        name: name ? name : '', 
        lat: this.latLng.lat,
        lng: this.latLng.lng,
        raw: this.rawAddress
      }, {
        wait: true,
        success: function(model, resp) {
          // TODO: Handle success in saving
        },
        failure: function(model, resp) {
          // TODO: Handle failure in saving
        }
      });
    }
  },

  deleteLocation: function(evt) {
    evt.preventDefault();
    var id = $(evt.target).data('location-id');
    var loc = this.collection.get(id);
    loc.destroy();
  }
});

storybase.builder.views.TagView = Backbone.View.extend({
  id: 'story-tags',

  templateSource: $('#tags-template').html(),

  events: {
    'change #tags': 'tagsChanged'
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
    this.collection = new storybase.collections.Tags(null, {
      story: this.model
    });
    this.collection.on("reset", this.setTags, this);
    if (_.isUndefined(this.model)) {
      this.dispatcher.on("ready:story", this.setStory, this);
    }
  },

  setStory: function(story) {
    this.model = story;
    this.collection.setStory(story);
  },

  render: function() {
    var s2opts = {
      ajax: {
        url: storybase.globals.API_ROOT + 'tags/',
        data: function(term, page) {
          return {
            'name__istartswith': term
          };
        },
        results: function(data, page) {
          var result = {
            results: []  
          };
          _.each(data.objects, function(tag) {
            result.results.push({
              id: tag.tag_id,
              text: tag.name,
              tagId: tag.tag_id
            });
          });
          return result;
        }
      },
      createSearchChoice: function(term, data) {
        return {id: term, text: term};
      },
      multiple: true,
      width: 'resolve'
    };
    this.collection.fetch();
    this.$el.html(this.template());
    this.$('#tags').select2(s2opts);
    this.delegateEvents();
    return this;
  },

  setTags: function() {
    var data = this.collection.map(function(tag) {
      return {
        id: tag.get('tag_id'),
        text: tag.get('name')
      };
    });
    this.$('#tags').select2('data', data);
  },

  tagsChanged: function(evt) {
    var data = {};
    var id;
    var model;
    if (evt.added) {
      if (evt.added.tagId) {
        // Existing tag
        data.tag_id = evt.added.tagId;
      }
      else {
        data.name = evt.added.text;
      }
      this.collection.create(data, {
        success: function(model) {
          evt.added.model = model;
        }
      });
    }
    if (evt.removed) {
      if (evt.removed.model) {
        model = evt.removed.model;
        id = evt.removed.model.id;
      }
      else if (evt.removed.tag_id) {
        model = this.collection.get(evt.removed.tag_id);
        id = evt.removed.tag_id;
      }
      else if (evt.removed.id) {
        model = this.collection.get(evt.removed.id);
        id = evt.removed.id;
      }
      model.url = storybase.globals.API_ROOT + 'tags/' + id + '/stories/' + this.model.id + '/';
      model.destroy();
    }
  }
});

storybase.builder.views.PublishView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.NavViewMixin, {
    id: 'share-publish',

    className: 'container',

    templateSource: $('#share-publish-template').html(),

    events: {
      'click .publish': 'handlePublish',
      'click .unpublish': 'handleUnpublish'
    },

    initialize: function() {
      var navViewOptions;

      this.dispatcher = this.options.dispatcher;
      this.template = Handlebars.compile(this.templateSource);
      this.featuredAssetView = new storybase.builder.views.FeaturedAssetView({
        story: this.model,
        dispatcher: this.dispatcher
      });
      this.legalView = new storybase.builder.views.LegalView({
        model: this.model,
        dispatcher: this.dispatcher
      });

      navViewOptions = {
        model: this.model,
        dispatcher: this.dispatcher,
        items: []
      };
      if (this.options.visibleSteps.review) {
        navViewOptions.items.push({
          id: 'workflow-nav-build-back',
          text: gettext("Back to Review"),
          path: 'review/'
        });
      }
      else {
        navViewOptions.items.push({
          id: 'workflow-nav-review-back',
          text: gettext("Continue Writing Story"),
          path: ''
        });
      }
      navViewOptions.items.push({
        id: 'workflow-nav-build-another-fwd',
        text: gettext("Tell Another Story"),
        path: '/build/',
        route: false
      });
      this.navView = new storybase.builder.views.WorkflowNavView(navViewOptions);
      
      if (_.isUndefined(this.model)) {
        this.dispatcher.on("ready:story", this.setStory, this);
      }
      this.dispatcher.on("accept:legal", this.handleAcceptLegal, this);
    },

    setStory: function(story) {
      this.model = story;
    },

    /**
     * Callback for when legal agreement is accepted.
     */
    handleAcceptLegal: function() {
      // Hide the legal form
      this.legalView.$el.hide();
      // Show the publish button
      this.togglePublished();
    },

    togglePublished: function() {
      var published = this.model ? (this.model.get('status') === "published") : false;
      if (published) {
        this.$('.status-published').show();
        this.$('.status-unpublished').hide();
      }
      else {
        this.$('.status-published').hide();
        if (this.legalView.acceptedLegalAgreement()) {
          this.$('.status-unpublished').show();
        }
      }
    },

    handlePublish: function(evt) {
      evt.preventDefault();
      console.debug('Entering handlePublish');
      var that = this;
      var triggerPublished = function(model, response) {
        that.dispatcher.trigger('publish:story', model);
        that.dispatcher.trigger('alert', 'success', 'Story published');
        that.togglePublished();
      };
      var triggerError = function(model, response) {
        that.dispatcher.trigger('error', "Error publishing story");
      };
      this.model.save({'status': 'published'}, {
        success: triggerPublished, 
        error: triggerError 
      });
    },

    handleUnpublish: function(evt) {
      evt.preventDefault();
      var that = this;
      var success = function(model, response) {
        that.dispatcher.trigger('alert', 'success', 'Story unpublished');
        that.togglePublished();
      };
      var triggerError = function(model, response) {
        that.dispatcher.trigger('error', "Error unpublishing story");
      };
      this.model.save({'status': 'draft'}, {
        success: success, 
        error: triggerError 
      });
    },

    getStoryUrl: function() {
      var url = this.model ? this.model.get('url') : '';
      var loc = window.location;
      if (url) {
        url = loc.protocol + "//" + loc.host + url;
      }
      return url;
    },

    render: function() {
      var context = {
        url: this.getStoryUrl(),
        title: this.model.get('title'),
        showSharing: this.options.showSharing
      };
      this.$el.html(this.template(context));
      this.$('.title').after(this.legalView.render().el);
      this.$('.status-published').after(this.featuredAssetView.render().el);
      if (this.legalView.acceptedLegalAgreement()) {
        this.legalView.$el.hide();
      }
      this.togglePublished();
      if (window.addthis) {
        // Render the addthis toolbox.  We have to do this explictly
        // since it wasn't in the DOM when the page was loaded.
        addthis.toolbox(this.$('.addthis_toolbox')[0], {
          // Don't append clickback URL fragment so users get a clean
          // URL when clicking the permalink button
          data_track_clickback: false
        });
      }
      this.navView.render();
      this.delegateEvents();
      return this;
    }
  })
);

storybase.builder.views.FeaturedAssetView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.FileUploadMixin, {
    id: 'featured-asset',

    events: {
      'click .change': 'clickChange',
      'click .add': 'clickAdd',
      'click .select-asset': 'clickSelectAsset',
      'click [type="reset"]': "cancel",
      'submit form.bbf-form': 'processForm'
    },

    templateSource: $('#featured-asset-template').html(),

    subTemplateSource: {
      'display': $('#featured-asset-display-template').html(),
      'select': $('#featured-asset-select-template').html(),
      'upload': $('#asset-uploadprogress-template').html()
    },

    getSubTemplate: function() {
      var state = this.getState();
      if (_.isUndefined(this.templates[state])) {
        if (this.subTemplateSource[state]) {
          this.templates[state] = Handlebars.compile(this.subTemplateSource[state]);
        }
        else {
          return null;
        }
      }
      return this.templates[state]; 
    },

    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      this.story = this.options.story;
      this.template = Handlebars.compile(this.templateSource);
      this.templates = {};
      this.form = this.getForm();

      if (_.isUndefined(this.story)) {
        this.dispatcher.on("ready:story", this.setStory, this);
      }
      else {
        this.model = this.story.getFeaturedAsset();
      }

      this.setInitialState();
    },

    setInitialState: function() {
      if (!_.isUndefined(this.model)) {
        this._state = 'display';
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

    getForm: function() {
      var form = new Backbone.Form({
        model: new storybase.models.Asset({
          type: 'image'
        })
      });
      return this.updateFormLabels(form); 
    },

    /** 
     * Update the view's form labels based on the asset type.
     */
    updateFormLabels: function(form) {
      if (form.schema.url) {
        form.schema.url.title = capfirst(gettext("enter the featured image URL"));
      }
      if (form.schema.image) {
        form.schema.image.title = capfirst(gettext("select the featured image from your own computer"));
      }
      return form;
    },

    setStory: function(story) {
      this.story = story;
      this.story.setFeaturedAssets(
        new storybase.collections.FeaturedAssets
      );
    },

    getImageAssetsJSON: function() {
      return _.map(this.story.assets.where({type: 'image'}),
        function(model) {
          return model.toJSON();
        }
      );
    },

    render: function() {
      var context = {};
      var state = this.getState();
      var subTemplate = this.getSubTemplate();
      if (this.model && (state === 'select' || state === 'display')) {
        context.model = this.model.toJSON();
      }
      if (state === 'select') {
        context.assets = this.getImageAssetsJSON();
      }
      if (state === 'add') {
        this.form.render().$el.append('<input type="reset" value="' + gettext("Cancel") + '" />').append('<input type="submit" value="' + gettext("Save Changes") + '" />');
      }
      this.$el.html(this.template(context));
      if (subTemplate) {
        this.$el.append(subTemplate(context));
      }
      if (state === 'add') {
        this.$el.append(this.form.el);
      }
      this.delegateEvents();
      return this;
    },

    /**
     * Event handler for submitting form
     */
    processForm: function(e) {
      e.preventDefault();
      var errors = this.form.validate();
      var file;
      var options = {};
      var that = this;
      if (!errors) {
        this.form.commit();
        file = this.form.model.get('image');
        if (file) {
          // Set a callback for saving the model that will upload the
          // image.
          options.success = function(model) {
            that.uploadFile(model, 'image', file, {
              progressHandler: that.handleUploadProgress,
              beforeSend: function() {
                that.setState('upload');
                that.render();
              },
              success: function(model, response) {
                that.setState('display');
                that.render();
              }
            });
          };
        }

        // Delete the image property.  We've either retrieved it for
        // upload or it was empty (meaning we don't want to change the
        // image.
        this.form.model.unset('image'); 
        this.saveModel(this.form.model, options);
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

    saveModel: function(model, options) {
      options = _.isUndefined(options) ? {} : options;
      var that = this;
      model.save(null, {
        success: function(model) {
          that.model = model;
          that.setState('display');
          that.render();
          that.story.assets.add(model);
          that.story.setFeaturedAsset(model);
          if (options.success) {
            options.success(model);
          }
        },
        error: function(model) {
          that.dispatcher.trigger('error', gettext('Error saving the featured image'));
        }
      });
    },

    clickChange: function(evt) {
      evt.preventDefault();
      this.setState('select').render();
    },

    clickAdd: function(evt) {
      evt.preventDefault();
      this.setState('add').render();
    },

    clickSelectAsset: function(evt) {
      evt.preventDefault();
      var id = $(evt.target).data('asset-id');
      this.model = this.story.assets.get(id);
      this.story.setFeaturedAsset(this.model);
      this.setState('display').render();
    },

    /**
     * Event handler for canceling form interaction
     */
    cancel: function(e) {
      e.preventDefault();
      if (this.model.isNew()) {
        this.setState('edit');
      }
      else {
        this.setState('display');
      }
      this.render();
    }
  })
);
