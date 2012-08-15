Namespace('storybase.builder.views');
Namespace.use('storybase.utils.capfirst');
Namespace.use('storybase.utils.getValue');
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
 */
storybase.builder.views.AppView = Backbone.View.extend({
  initialize: function() {
    // Common options passed to sub-views
    var commonOptions = {};
    var buildViewOptions;
    var shareViewOptions;
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
    this.helpView = new storybase.builder.views.HelpView(commonOptions);

    if (this.model) {
      commonOptions.model = this.model;
    }
    buildViewOptions = _.extend(commonOptions, {
      assetTypes: this.options.assetTypes,
      layouts: this.options.layouts,
      help: this.options.help
    });
    shareViewOptions = _.extend(commonOptions, {
      places: this.options.places,
      topics: this.options.topics,
      organizations: this.options.organizations,
      projects: this.options.projects
    });
    // Store subviews in an object keyed with values of this.activeStep
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
    this.updateStep('build');
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
    //this.$el.height($(window).height());
    this.$('#app').empty();
    this.$('#app').append(activeView.render().$el);
    // Some views have things that only work when the element has been added
    // to the DOM. The pattern for handling this comes courtesy of
    // http://stackoverflow.com/questions/9350591/backbone-using-jquery-plugins-on-views
    if (activeView.onShow) {
      activeView.onShow();
    }
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
    // Check for duplicate messages and only show the message
    // if it's different.
    if (!(level === this.lastLevel && msg === this.lastMessage)) {
      this.$('.alerts').prepend(view.render().el);
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
      title: gettext('Build'),
      callback: 'selectStep',
      visible: true,
      path: ''
    },
    {
      id: 'data',
      title: gettext('Add Data'),
      callback: 'selectStep',
      visible: false,
      path: 'data/'
    },
    {
      id: 'review',
      title: gettext('Review'),
      callback: 'selectStep',
      visible: false,
      path: 'review/'
    },
    {
      id: 'share',
      title: gettext('Share'),
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
    this.dispatcher.on('ready:story', this.handleStorySave, this);
    this.dispatcher.on('save:story', this.handleStorySave, this);
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


  handleStorySave: function(story) {
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
    this.dispatcher.on('ready:story', this.handleStorySave, this);
    this.dispatcher.on('save:story', this.handleStorySave, this);
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
  
  handleStorySave: function(story) {
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
 * Next/forward buttons for each section
 */
// TODO: Merge this functionality with MenuView
storybase.builder.views.WorkflowNavView = Backbone.View.extend({ 
  tagName: 'div',

  className: 'workflow-nav',

  itemTemplateSource: $('#workflow-nav-item-template').html(),

  items: {},

  events: function() {
    var events = {};
    _.each(this.items, function(item) {
      if (item.route !== false) {
        events['click #' + item.id] = _.isUndefined(item.callback) ? this.handleClick : item.callback;
      }
    }, this);
    return events;
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.forward = this.options.forward;
    this.back = this.options.back;
    this.items = _.isUndefined(this.options.items) ? this.items : this.options.items;
    this.itemTemplate = Handlebars.compile(this.itemTemplateSource);
    if (_.isUndefined(this.model)) {
      this.dispatcher.on("ready:story", this.setStory, this);
    }
  },

  setStory: function(story) {
    this.model = story;
    this.render();
  },

  getHref: function(itemOptions) {
    if (itemOptions.route !== false) {
      return storybase.builder.globals.APP_ROOT + this.model.id + '/' + itemOptions.path;
    }
    else {
      return itemOptions.path;
    }
  },

  renderItem: function(itemOptions) {
    var enabled = _.isFunction(itemOptions.enabled) ? itemOptions.enabled() : true;
    this.$el.append(this.itemTemplate({
      id: itemOptions.id,
      class: (enabled ? "" : " disabled"),
      title: itemOptions.title,
      href: this.getHref(itemOptions)
    }));
  },

  getItem: function(id) {
    return _.filter(this.items, function(item) {
      return item.id === id;
    })[0];
  },

  getVisibleItems: function() {
    return _.filter(this.items, function(item) {
      return _.isUndefined(item.visible) ? true : getValue(item.visible); 
    });
  },

  render: function() {
    this.$el.empty();
    _.each(this.getVisibleItems(), function(item) {
      this.renderItem(item);
    }, this);
    this.delegateEvents();

    return this;
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
    this.navView = new storybase.builder.views.WorkflowNavView({
      model: this.model,
      dispatcher: this.dispatcher,
      items: [
        {
          id: 'workflow-nav-data-fwd',
          title: gettext("Add Data to Your Story"),
          path: 'data/',
          enabled: _.bind(function() {
            return !this.model.isNew();
          }, this)
        }
      ],
    });
    this._editViews = [];

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
    this.dispatcher.on("save:story", this.setTitle, this);
    this.dispatcher.on("ready:story", this.setTitle, this);
    this.dispatcher.on("created:section", this.handleCreateSection, this);

    _.bindAll(this, 'setTemplateStory', 'setTemplateSections', 'createSectionEditView');

    if (!this.model.isNew()) {
      this.model.sections.fetch();
      this.model.unusedAssets.fetch();
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
    var view = new storybase.builder.views.SectionEditView({
      dispatcher: this.dispatcher,
      model: section,
      collection: this._editViews,
      story: this.model,
      assetTypes: this.options.assetTypes,
      layouts: this.options.layouts,
      defaultHelp: this.help.where({slug: 'new-section'})[0]
    }); 
    this._editViews.push(view);
    return view;
  },

  createEditViews: function() {
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
    this._editViews.push(storyEditView);
    this.model.sections.each(this.createSectionEditView); 
    this._editViews.push(callEditView);
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
      that.sectionListView.$el.before(view.render().$el.hide());
    });
    if (this._editViews.length && options.showFirst) {
      this._editViews[0].show();
    }
  },

  render: function() {
    console.info('Rendering builder view');
    var that = this;
    this.$el.prepend(this.unusedAssetView.render().$el.hide());
    this.$el.prepend(this.lastSavedView.render().el);
    this.$el.append(this.sectionListView.render().el);
    this.renderEditViews();
    // TODO: properly place this
    this.$el.append(this.navView.render().el);
    return this;
  },

  /**
   * Things that need to happen after the view's element has
   * been added to the DOM.
   *
   * This is called from upstream views.
   */
  onShow: function() {
    // Recalculate the width of the section list view.
    this.sectionListView.setWidth();
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
          trigger: true 
        });
        model.saveSections();
        // Re-render the navigation view to enable the button
        that.navView.render();
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
    this.model = this.options.model;
    this._thumbnailViews = {};
    this._sortedThumbnailViews = [];
    this._sectionsFetched = false;
    this._thumbnailsAdded = false;
    this._doScroll = false;
    this._thumbnailWidth = 0;

    this.template = Handlebars.compile(this.templateSource);

    this.dispatcher.on("do:remove:section", this.removeSection, this);
    this.dispatcher.on("ready:story", this.addSectionThumbnails, this);

    _.bindAll(this, 'addSectionThumbnail');

    this.$el.html(this.template());
  },

  addSectionThumbnail: function(section, index) {
    var view = new storybase.builder.views.SectionThumbnailView({
      dispatcher: this.dispatcher,
      model: section
    });
    index = _.isUndefined(index) ? this._sortedThumbnailViews.length - 1 : index + 1; 
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
      this.dispatcher.trigger("select:thumbnail", this._sortedThumbnailViews[0]);
      this.$('.sections').sortable({
        items: 'li:not(.pseudo)'
      });
    }
 
    this.setWidth();
    this.$('.sections-clip').css({overflow: 'hidden'});
    this.delegateEvents();

    return this;
  },

  getThumbnailView: function(section) {
    return this._thumbnailViews[section.id];
  },

  removeThumbnailView: function(view) {
    var index = _.indexOf(this._sortedThumbnailViews, view);
    if (view && view.isHighlighted()) {
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
      root: true
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
    // TODO: Use the 'blind' easing function to show/hide this
    this.$('.sections-container').toggle();
    $(evt.target).toggleClass('opened');
    $(evt.target).toggleClass('closed');
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
    },

    show: function(id) {
      id = _.isUndefined(id) ? this.pseudoSectionId : id;
      if (id == this.pseudoSectionId) {
        console.debug("Showing editor for pseduo-section " + this.pseudoSectionId);
        this.$el.show();
        this.dispatcher.trigger('do:show:help', false, this.help.toJSON()); 
      }
      else {
        console.debug("Hiding editor for pseduo-section " + this.pseudoSectionId);
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
    "change .title input": 'change',
    "change select.layout": 'change'
  },

  initialize: function() {
    _.defaults(this.options, this.defaults);
    this.dispatcher = this.options.dispatcher;
    this.story = this.options.story;
    this.layouts = this.options.layouts;
    this.defaultHelp = this.options.defaultHelp;
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
    console.debug('Rendering asset views');
    var that = this;
    this.$('.storybase-container-placeholder').each(function(index, el) {
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
      tooltip: gettext('Click to edit title'),
      onblur: 'submit'
    });
    return this;
  },

  show: function(section) {
    section = _.isUndefined(section) ? this.model : section;
    var help = this.model.get('help') || this.defaultHelp.toJSON();
    if (section == this.model) {
      console.debug('showing section ' + section.get('title'));
      this.$el.show();
      this.dispatcher.trigger('do:show:help', false, help); 
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
  }
});

storybase.builder.views.SectionAssetEditView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.FileUploadMixin, 
           storybase.builder.views.RichTextEditorMixin, {
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
      else if (state === 'upload') {
        return $('#section-asset-uploadprogress-template').html();
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
      'submit form.bbf-form': 'processForm',
      'drop': 'handleDrop'
    },

    states: ['select', 'display', 'edit'],

    initialize: function() {
      console.debug("Initializing new section asset edit view");
      this.container = this.options.container;
      this.dispatcher = this.options.dispatcher;
      this.assetTypes = this.options.assetTypes;
      this.section = this.options.section;
      this.story = this.options.story;
      if (_.isUndefined(this.model)) {
        this.model = new storybase.models.Asset();
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

    render: function() {
      console.debug("Rendering section asset edit view");
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
      this.setClass();
      if (state == 'select') {
        this.$el.droppable();
      }
      if (state == 'display') {
        if (!this.$('.caption').length && this.model.formFieldVisible('caption', this.model.get('type'))) {
          this.$el.append($('<div class="caption"></div>'));
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
        this.$el.append(this.form.el);
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

    handleDrop: function(event, ui) {
      console.debug("Asset dropped");
      var id = ui.draggable.data('asset-id');
      this.model = this.story.unusedAssets.get(id);
      this.story.unusedAssets.remove(this.model);
      if (!this.story.unusedAssets.length) {
        this.dispatcher.trigger('has:assetlist', false);
      }
      this.setState('display');
      this.dispatcher.trigger("do:add:sectionasset", this.section, this.model, this.container);
      this.render();
    }
  })
);

storybase.builder.views.DataView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.FileUploadMixin, {
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
            title: gettext("Continue Writing Story"),
            path: ''
          },
          {
            id: 'workflow-nav-review-fwd',
            title: gettext("Review"),
            path: 'review/'
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
        this.$el.append(this.navView.render().el);
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

storybase.builder.views.ReviewView = Backbone.View.extend({
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
          id: 'workflow-nav-data-back',
          title: gettext("Back to Add Data"),
          path: 'data/'
        },
        {
          id: 'workflow-nav-share-legal-fwd',
          title: gettext("Share My Story"),
          path: 'share/legal/',
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
    this.$el.append(this.navView.render().el);
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
});

storybase.builder.views.ShareView = Backbone.View.extend({
  id: 'share',

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
    this.activeStep = null;

    this.subviews = {
      'legal': new storybase.builder.views.LegalView({
        dispatcher: this.dispatcher,
        model: this.model
      }),
      'tagging': new storybase.builder.views.TaxonomyView({
        dispatcher: this.dispatcher,
        model: this.model,
        places: this.options.places,
        topics: this.options.topics,
        organizations: this.options.organizations,
        projects: this.options.projects
      }),
      'publish': new storybase.builder.views.PublishView({
        dispatcher: this.dispatcher,
        model: this.model
      }),
    };

    this.dispatcher.on('select:workflowstep', this.updateStep, this);
  },

  updateStep: function(step, subStep) {
    if (step === 'share' && _.include(_.keys(this.subviews), subStep)) {
      this.activeStep = subStep;
      this.render();
      this.onShow();
    }
  },

  getActiveView: function() {
    return this.activeStep ? this.subviews[this.activeStep] : this.subviews['legal'];
  },

  render: function() {
    console.info('Rendering share view');
    var context = {};
    var subView = this.getActiveView(); 
    _.each(this.subviews, function(view, subStep) {
      if (subStep != this.activeStep) {
        view.$el.remove();
      }
    }, this);
    this.$el.append(subView.render().el);
    return this;
  },

  onShow: function() {
    var view = this.getActiveView();
    if (view.onShow) {
      view.onShow();
    }
  }
});

storybase.builder.views.LegalView = Backbone.View.extend({
  id: 'share-legal',

  templateSource: $('#share-legal-template').html(),

  events: {
    'change input[name=license]': 'changeLicenseAgreement'
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
    // IMPORTANT: Need to bind validate to this view before passing
    // it as a callback to the WorkflowNavView instance
    _.bindAll(this, 'validate');
    this.navView = new storybase.builder.views.WorkflowNavView({
      model: this.model,
      dispatcher: this.dispatcher,
      items: [
        {
          id: 'workflow-nav-review-back',
          title: gettext("Back to Review"),
          path: 'review/'
        },
        {
          id: 'workflow-nav-share-tagging-fwd',
          title: gettext("Continue"),
          path: 'share/tagging/',
          validate: this.validate
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
    this.$el.append(this.form.render().el);
    this.updateFormDefaults();
    this.$el.append(this.navView.render().el);
    this.delegateEvents();

    return this;
  },

  changeLicenseAgreement: function(evt) {
    this.agreedLicense = $(evt.target).prop('checked');
    this.setRadioEnabled();
  }
});

storybase.builder.views.TaxonomyView = Backbone.View.extend({
  id: 'share-taxonomy',

  templateSource: $('#share-taxonomy-template').html(),

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
    this.navView = new storybase.builder.views.WorkflowNavView({
      model: this.model,
      dispatcher: this.dispatcher,
      items: [
        {
          id: 'workflow-nav-share-legal-back',
          title: gettext("Back to Legal Agreements"),
          path: 'share/legal/'
        },
        {
          id: 'workflow-nav-share-publish-fwd',
          title: gettext("Continue"),
          path: 'share/publish/'
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
        editorAttrs: _.extend(editorAttrs, {placeholder: gettext("Click to select topics")})
      },
      places: { 
        type: 'Select', 
        options: placesOptions, 
        editorAttrs: _.extend(editorAttrs, {placeholder: gettext("Click to select places")})
      },
      organizations: {
        type: 'Select',
        options: organizationsOptions,
        editorAttrs: _.extend(editorAttrs, {placeholder: gettext("Click to select organizations")})
      },
      projects: {
        type: 'Select',
        options: projectsOptions,
        editorAttrs: _.extend(editorAttrs, {placeholder: gettext("Click to select projects")})
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
    this.$el.append(this.navView.render().el);

    return this;
  },

  onShow: function() {
    this.addLocationView.onShow();
  }
});

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
    console.debug(id);
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
    console.debug(evt);
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
      console.debug(model);
      model.url = storybase.globals.API_ROOT + 'tags/' + id + '/stories/' + this.model.id + '/';
      model.destroy();
    }
  }
});

storybase.builder.views.PublishView = Backbone.View.extend({
  id: 'share-publish',

  templateSource: $('#share-publish-template').html(),

  events: {
    'click .publish': 'handlePublish',
    'click .unpublish': 'handleUnpublish'
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
    this.navView = new storybase.builder.views.WorkflowNavView({
      model: this.model,
      dispatcher: this.dispatcher,
      items: [
        {
          id: 'workflow-nav-share-tagging-back',
          title: gettext("Back to Tagging"),
          path: 'share/tagging/'
        },
        {
          id: 'workflow-nav-build-another-fwd',
          title: gettext("Tell Another Story"),
          path: '/build/',
          route: false
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

  togglePublished: function() {
    var published = this.model ? (this.model.get('status') === "published") : false;
    if (published) {
      this.$('.status-published').show();
      this.$('.status-unpublished').hide();
    }
    else {
      this.$('.status-published').hide();
      this.$('.status-unpublished').show();
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
      title: this.model.get('title')
    };
    this.$el.html(this.template(context));
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
    this.$el.append(this.navView.render().el);
    this.delegateEvents();
    return this;
  }
});
