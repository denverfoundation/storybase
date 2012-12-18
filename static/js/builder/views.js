Namespace('storybase.builder.views');
Namespace.use('storybase.utils.capfirst');
Namespace.use('storybase.utils.geocode');

/**
 * Default visible steps of the story builder workflow.  
 *
 * These are usually passed to AppView when it is initialized.  However,
 * these defaults are provided to better document the behavior of the
 * app and for testing independent of the server-side code.
 */
storybase.builder.views.VISIBLE_STEPS = {
  'build': true,
  'data': true, 
  'tag': true,
  'review': true,
  'publish': true
};

/**
 * Is the browser some version of Microsoft Internet Explorer?
 *
 * HACK: Browser detection is bad, but our work-around for #415 should only
 * apply to MSIE and we can't determine this by feature detection.
 */
storybase.builder.views.MSIE = ($.browser !== undefined) && ($.browser.msie === true);

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
  options: {
    alertsEl: '#alerts',
    browserSupportMessage: "This site works best on a modern browser", 
    drawerEl: '#drawer-container',
    headerEl: '#header',
    language: 'en',
    partials: {
      'help-icon': $('#help-icon-partial').html()
    },
    subNavContainerEl: '#subnav-bar-contents',
    subviewContainerEl: '#app',
    toolsContainerEl: '#title-bar-contents',
    visibleSteps: storybase.builder.views.VISIBLE_STEPS, 
    workflowContainerEl: '#workflow-bar-contents'
  },

  registerPartials: function() {
    _.each(this.options.partials, function(tmplSrc, name) {
      Handlebars.registerPartial(name, tmplSrc);
    });
  },

  initialize: function() {
    // Common options passed to sub-views
    var commonOptions = {
      dispatcher: this.options.dispatcher,
      language: this.options.language,
      startOverUrl: this.options.startOverUrl,
      visibleSteps: this.options.visibleSteps
    };
    var buildViewOptions;
    var $toolsContainerEl = this.$(this.options.toolsContainerEl);
    this.$workflowContainerEl = this.$(this.options.workflowContainerEl);

    // Register some partials used across views with Handlebars
    this.registerPartials();

    this.dispatcher = this.options.dispatcher;
    // The currently active step of the story building process
    // This will get set by an event callback 
    this.activeStep = null; 

    // Initialize a view for the tools menu
    this.toolsView = new storybase.builder.views.ToolsView(
      _.clone(commonOptions)
    );
    $toolsContainerEl.append(this.toolsView.el);

    this.helpView = new storybase.builder.views.HelpView(
      _.clone(commonOptions)
    );
    this.drawerView = new storybase.builder.views.DrawerView({
      dispatcher: this.dispatcher
    });
    this.drawerView.registerView(this.helpView);

    if (this.model) {
      commonOptions.model = this.model;
    }

    // Initialize the view for the workflow step indicator
    this.workflowStepView = new storybase.builder.views.WorkflowStepView(
      _.clone(commonOptions)
    );
    this.$workflowContainerEl.append(this.workflowStepView.el);

    buildViewOptions = _.defaults({
      assetTypes: this.options.assetTypes,
      containerTemplates: this.options.containerTemplates,
      forceTour: this.options.forceTour,
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
      showTour: this.options.showTour,
      siteName: this.options.siteName
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
      this.subviews.data = new storybase.builder.views.DataView(
        _.clone(commonOptions)
      );
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
      this.subviews.review = new storybase.builder.views.ReviewView(
        _.clone(commonOptions)
      );
    }
    if (this.options.visibleSteps.publish) {
      this.subviews.publish =  new storybase.builder.views.PublishView(
        _.defaults({
          showSharing: this.options.showSharing,
          licenseEndpoint: this.options.licenseEndpoint
        }, commonOptions)
      );
    }

    // IMPORTANT: Create the builder view last because it triggers
    // events that the other views need to listen to
    this.subviews.build = new storybase.builder.views.BuilderView(buildViewOptions);
    this.lastSavedView = new storybase.builder.views.LastSavedView({
      dispatcher: this.dispatcher,
      lastSaved: this.model ? this.model.get('last_edited'): null
    });
    this.$workflowContainerEl.append(this.lastSavedView.render().el);

    // Initialize the properties that store the last alert level
    // and message.
    this.lastLevel = null;
    this.lastMessage = null;

    // Bind callbacks for custom events
    this.dispatcher.on("open:drawer", this.openDrawer, this);
    this.dispatcher.on("close:drawer", this.closeDrawer, this);
    this.dispatcher.on("select:template", this.setTemplate, this);
    this.dispatcher.on("select:workflowstep", this.updateStep, this); 
    this.dispatcher.on("error", this.error, this);
    this.dispatcher.on("alert", this.showAlert, this);
  },

  openDrawer: function() {
    this.$el.addClass('drawer-open');
  },

  closeDrawer: function() {
    this.$el.removeClass('drawer-open');
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
    var activeView;
    // Checking that step is different from the active step is
    // required for the initial saving of the story.  The active view
    // has already been changed by ``this.setTemplate`` so we don't
    // want to re-render.  In all other cases the changing of the 
    // active view is initiated by the router triggering the ``select:
    // workflowstep`` signal
    if (this.activeStep != step) {
      console.debug('Updating active step to ' + step);
      activeView = this.getActiveView();
      if (activeView && activeView.onHide) {
        activeView.onHide();
      }
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

  /**
   * Update the next/previous workflow step buttons
   */
  renderWorkflowNavView: function(activeView) {
    if (this._activeWorkflowNavView) {
      // Remove the previous active workflow nav view
      this._activeWorkflowNavView.$el.remove();
    };
    // Update the workflow nav view
    this._activeWorkflowNavView = _.isUndefined(activeView.getWorkflowNavView) ? null: activeView.getWorkflowNavView();
    if (this._activeWorkflowNavView) {
      this.workflowStepView.$el.after(this._activeWorkflowNavView.el);
    }
  },

  renderSubNavView: function(activeView) {
    var $subNavContainerEl = this.$(this.options.subNavContainerEl);
    if (this._activeSubNavView) {
      // Remove the previous subnav view
      this._activeSubNavView.$el.remove();
    }
    this._activeSubNavView = _.isUndefined(activeView.getSubNavView) ? null : activeView.getSubNavView();
    if (this._activeSubNavView) {
      $subNavContainerEl.append(this._activeSubNavView.el);  
    }
  },

  /**
   * Adjust the top padding of the subview container view to accomodate the
   * header.
   *
   * @param {Array} $el jQuery object for element that needs to have its
   *   padding adjusted.
   *
   * This has to be done dynamically because the header is different
   * heights based on different workflow steps. 
   */
  pushDown: function($el) {
    var $header = this.$(this.options.headerEl);
    var orig = $el.css('margin-top');
    var headerBottom = $header.offset().top + $header.outerHeight();
    $el.css('margin-top', headerBottom);
    return this;
  },

  render: function() {
    console.debug('Rendering main view');
    var activeView = this.getActiveView();
    var $container = this.$(this.options.subviewContainerEl);
    this.renderWorkflowNavView(activeView);
    this.renderSubNavView(activeView);
    $container.empty();
    $container.append(activeView.render().$el);
    this.pushDown($container);
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
    this.drawerView.setElement(this.options.drawerEl).render();
    this.pushDown(this.drawerView.$el);
    if (!this.checkBrowserSupport()) {
      this.showAlert('error', this.options.browserSupportMessage, null);
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

  /**
   * Show an alert message.
   *
   * @param {String} level Message level. Used to style the message.
   * @param {String} msg Message text.
   * @param {Integer|null} [timeout=15000] Milliseconds to show the message
   *   before it is hidden. If null, the message remains visible.
   *
   */
  showAlert: function(level, msg, timeout) {
    timeout = _.isUndefined(timeout) ? 15000 : timeout;
    var $el = this.$(this.options.alertsEl);
    var numAlerts = $el.children().length;
    var view = new storybase.builder.views.AlertView({
      level: level,
      message: msg
    });
    // Check for duplicate messages and only show the message
    // if it's different.
    if (!(level === this.lastLevel && msg === this.lastMessage && numAlerts > 0)) {
      $el.prepend(view.render().el);
      if (timeout) {
        view.$el.fadeOut(timeout, function() {
          $(this).remove();
        });
      }
    }
    this.lastLevel = level;
    this.lastMessage = msg;
  },

  /**
   * Check support for various required browser features.
   *
   * @returns {Boolean} true if all required browser features are present,
   *   otherwise, false.
   *
   * Eventually, support for these features should be worked around, at least
   * for IE9, but for launch, we decided to just show a message.
   *
   */
  checkBrowserSupport: function() {
    // Check for the various File API support.
    if (Modernizr.filereader) {
    }
    else {
      // The File APIs are not fully supported in this browser
      return false;
    }

    // Check for pushState support
    if (Modernizr.history) {
      // pushState supported
    }
    else {
      return false;
    }

    // If we haven't returned yet, we have support for everything needed
    return true; 
  }
});

storybase.builder.views.DrawerButtonView = Backbone.View.extend({
  //tagName: 'button',
  tagName: 'div',

  className: 'btn',

  events: {
    'click': 'handleClick'
  },

  initialize: function() {
    this.buttonId = this.options.buttonId;
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.options.templateSource);
  },

  render: function() {
    this.$el.attr('title', this.options.title);
    this.$el.html(this.options.text);
    this.delegateEvents();
    return this;
  },

  handleClick: function(evt) {
    this.dispatcher.trigger('do:toggle:drawer', this.options.parent);
    if (this.options.callback) {
      this.options.callback(evt);
    }
  },
});

/**
 * View to toggle other views in a slide-out drawer.
 */
storybase.builder.views.DrawerView = Backbone.View.extend({
  options: {
    templateSource: $('#drawer-template').html(),
    controlsEl: '#drawer-controls',
    contentsEl: '#drawer-contents'
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.dispatcher.on('register:drawerview', this.registerView, this);
    this.dispatcher.on('unregister:drawerview', this.unregisterView, this);
    this.dispatcher.on('do:toggle:drawer', this.toggle, this);

    this.template = Handlebars.compile(this.options.templateSource);
    this.buttonTemplate = Handlebars.compile(this.options.buttonTemplateSource);
    // The state of the drawer
    this._open = false;
    // Store the button views 
    this._buttons = {};
    // Store the order of buttons
    this._buttonIds = [];
    this._subviews = {};
  },

  /**
   * Register a view with the drawer.
   *
   * @param {Object} view Backbone view 
   *
   * The view must have the following properties:
   *   drawerButton: an instance (or function returning an instance) of 
   *     DrawerButtonView
   *   drawerOpenEvents: a string with a space-separated list of events that
   *     will open the drawer and show the view.  This provides a
   *     means of showing a view in the drawer other than clicking the
   *     drawer button.
   *   drawerCloseEvents: a string with a space-separated list of events
   *     that will close the drawer.  This provides a means of hiding a
   *     view in a drawer other htan clicking the drawer button.
   *   show: A method that shows the view
   *   hide: A method that hides the view
   */
  registerView: function(view) {
    this.addButton(_.result(view, 'drawerButton'));
    this.dispatcher.on(_.result(view, 'drawerOpenEvents'), function() {
      this.open(view);
    }, this);
    this.dispatcher.on(_.result(view, 'drawerCloseEvents'), function() {
      this.close(view);
    }, this);
    if (view.extraEvents) {
      _.each(_.result(view, 'extraEvents'), function(fn, evt) {
        this.dispatcher.on(evt, fn, this);
      }, this);
    }
    this._subviews[view.cid] = view;
    this.render();
  },

  unregisterView: function(view) {
    this.removeButton(_.result(view, 'drawerButton'));
    this.dispatcher.off(_.result(view, 'drawerOpenEvents'));
    this.dispatcher.off(_.result(view, 'drawerCloseEvents'));
    _.each(_.result(view, 'extraEvents'), function(fn, evt) {
      this.dispatcher.off(evt, fn, this);
    }, this);
    this._subviews = _.omit(this._subviews, view.cid);
    this.render();
  },

  addButton: function(button) {
    this._buttons[button.buttonId] = button;
    this._buttonIds.push(button.buttonId);
  },

  removeButton: function(button) {
    // Remove this button from the list of buttons
    this._buttonIds = _.without(this._buttonIds, button.buttonId);
    this._buttons = _.omit(this._buttons, button.buttonId);
  },

  renderButtons: function() {
    var $controlsEl = this.$(this.options.controlsEl);
    _.each(this._buttons, function(button) {
      button.render().$el.appendTo($controlsEl);
    }, this);
    return this;
  },

  renderSubViews: function() {
    var $contentsEl = this.$(this.options.contentsEl);
    _.each(this._subviews, function(view) {
      $contentsEl.append(view.render().$el);
    }, this);
    return this;
  },

  render: function() {
    this.$el.html(this.template());
    this.renderButtons();
    this.renderSubViews();
    return this;
  },

  activeView: function(view) {
    if (!_.isUndefined(view)) {
      this._activeView = view;
    }
    return this._activeView;
  },

  // Show the active view and hide all the other views
  showActiveView: function(view) {
    var activeView = this.activeView(view);
    _.each(this._subviews, function(view) {
      if (view.cid === activeView.cid) {
        view.show();
      }
      else {
        view.hide();
      }
    }, this);
  },

  open: function(view) {
    this._open = true;
    if (view) {
      this.showActiveView(view);
    }
    this.$(this.options.contentsEl).show();
    this.dispatcher.trigger('open:drawer');
    return this;
  },

  close: function(view) {
    this._open = false;
    this.$(this.options.contentsEl).hide();
    this.dispatcher.trigger('close:drawer');
    return this;
  },

  isOpen: function() {
    return this._open;
  },
  
  toggle: function(view) {
    var activeView = this.activeView();
    if (this.isOpen()) {
      if (activeView.cid === view.cid) {
        this.close();
      }
      else {
        this.showActiveView(view);
      }
    }
    else {
      this.open(view);
    }
    return this;
  }
});

storybase.builder.views.HelpDrawerMixin = {
  drawerButton: function() {
    if (_.isUndefined(this.drawerButtonView)) {
      this.drawerButtonView = new storybase.builder.views.DrawerButtonView({
        dispatcher: this.dispatcher,
        buttonId: 'help',
        title: gettext('Help'),
        text: gettext('Help'),
        parent: this
      });
    }
    return this.drawerButtonView;
  },

  drawerOpenEvents: 'do:show:help',

  drawerCloseEvents: 'do:hide:help'
};

storybase.builder.views.HelpView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.HelpDrawerMixin, {
    tagName: 'div',

    className: 'help',

    options: {
      templateSource: $('#help-template').html()
    },

    events: {},

    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      this.help = null;
      this.template = Handlebars.compile(this.options.templateSource);

      this.$el.hide();

      this.dispatcher.on('do:show:help', this.show, this);
      this.dispatcher.on('do:set:help', this.set, this);
      this.dispatcher.on('do:hide:help', this.hide, this);
    },

    /**
     * Show the help text.
     *
     * @help object help Updated help information.  The object should have
     *     a body property and optionally a title property.
     *
     * @returns object This view.
     */
    show: function(help) {
      if (!_.isUndefined(help)) {
        // A new help object was sent with the signal, update
        // our internal value
        this.set(help);
      }
      if (this.help) {
        this.render();
        this.delegateEvents();
        this.$el.show();
      }
      return this;
    },

    hide: function() {
      this.$el.hide();
    },

    set: function(help) {
      this.help = help;
      this.render();
    },

    render: function() {
      var context = _.extend({
        'autoShow': this.autoShow
      }, this.help);
      this.$el.html(this.template(context));
      return this;
    }
  })
);

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
    var cssClass = itemOptions.className || "";
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
      className: this.getItemClass(itemOptions),
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
    if (!$button.hasClass("disabled") && !$button.parent().hasClass("disabled") && valid) { 
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
  tagName: 'ol',

  id: 'workflow-step',

  className: 'nav',

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
        title: gettext("Construct your story using text, photos, videos, data visualizations, and other materials"),
        text: gettext("Build"),
        visible: true,
        selected: false,
        path: ''
      });
    }
    if (this.options.visibleSteps.data) {
      items.push({
        id: 'data',
        title: gettext("Upload or link to source data referenced in your story’s charts, maps, graphs and visualizations"),
        text: gettext('Add Data'),
        visible: true,
        enabled: 'isStorySaved',
        selected: false,
        path: 'data/'
      });
    }
    if (this.options.visibleSteps.tag) {
      items.push({
        id: 'tag',
        title: gettext("Label your story with topics and places so that people can easily discover it on Floodlight"),
        text: gettext('Tag'),
        visible: true,
        enabled: 'isStorySaved',
        selected: false,
        path: 'tag/',
      });
    }
    if (this.options.visibleSteps.review) {
      items.push({
        id: 'review',
        //title: gettext("Make sure your story is ready to go with spellcheck and other tools"),
        title: gettext("Make sure your story is ready to go"),
        text: gettext('Review'),
        visible: true,
        enabled: 'isStorySaved',
        selected: false,
        path: 'review/'
      });
    }
    if (this.options.visibleSteps.publish) {
      items.push({
        id: 'publish',
        title: gettext("Post your story to Floodlight and your social networks"),
        text: gettext('Publish/Share'),
        visible: true,
        enabled: 'isStorySaved',
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

  id: 'tools',

  className: 'nav',

  _initItems: function() {
    return [
      {
        id: 'preview',
        title: gettext("Preview your story in a new window"),
        text: gettext('Preview'),
        callback: 'previewStory',
        visible: false, 
        enabled: 'isStorySaved'
      },
      {
        id: 'start-over',
        title: gettext("Leave your story and start a new one with a different template"),
        text: gettext('Start Over'),
        path: this.options.startOverUrl,
        visible: false 
      },
      {
        id: 'exit',
        title: gettext("Leave the Story Builder and go back to the homepage. You can always return later"),
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

    this.dispatcher.on('ready:story', this.handleStorySave, this);
    this.dispatcher.on('save:story', this.handleStorySave, this);
    this.dispatcher.on("select:workflowstep", this.updateStep, this);
  },

  previewStory: function(evt) {
    if (!$(evt.target).hasClass("disabled")) {
      var url = '/stories/' + this.storyId + '/viewer/';
      window.open(url);
    }
    evt.preventDefault();
  },

  toggleHelp: function(evt) {
    evt.preventDefault();
    this.dispatcher.trigger('do:show:help');
  },
  
  handleStorySave: function(story) {
    var item = this.getItem('preview');
    if (!story.isNew() && _.isUndefined(this.storyId)) {
      this.storyId = story.id; 
      item.path = '/stories/' + this.storyId + '/viewer/';
    }
    item.visible = true;
    this.render();
  },

  updateVisible: function() {
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
  },

  isStorySaved: function() {
    return !_.isUndefined(this.storyId)
  }
});

/**
 * Story template selector
 */
storybase.builder.views.SelectStoryTemplateView = Backbone.View.extend({
  tagName: 'ul',
 
  className: 'story-templates view-container',

  templateSource: $('#story-template-list-template').html(),

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
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
    this.$el.html(this.template());
    this.collection.each(this.addTemplateEntry);
    return this;
  }
});

/**
 * Story template listing
 */
storybase.builder.views.StoryTemplateView = Backbone.View.extend({
  tagName: 'li',

  attributes: function() {
    return {
      // Use this instead of the className property so we can set the class
      // dynamically when the view is instantiated based on the model's 
      // slug
      'class': 'template ' + this.model.get('slug') 
    };
  },

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

/**
 * Class to encapsulate builder tour logic.
 */
storybase.builder.views.BuilderTour = function(options) {
  this.options = _.extend({}, options);
  this.initialize.apply(this, arguments);
};

_.extend(storybase.builder.views.BuilderTour.prototype, {
  // Load some of the longer guider bodies from a template, because
  // the text is too cumbersome to have inline.  Should all of the
  // bodies be in a template for consistency?
  //
  // The properties of this object correspond to the ids defined in
  // the guiders
  templateSource: {
    'workflow-step-guider': $('#workflow-step-guider-template').html(),
    'section-manipulation-guider': $('#section-manipulation-guider-template').html(),
    'exit-guider': $('#exit-guider-template').html()
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
    this._initTemplates();
  },

  /**
   * Precompile the templates.
   */
  _initTemplates: function() {
    this.template = {};
    _.each(this.templateSource, function(source, id) {
      this.template[id] = Handlebars.compile(source);
    }, this);
  },

  /**
   * Move a guider's element to the left or right.
   */
  nudge: function($guiderEl, amount) {
    var guiderElemLeft = parseInt($guiderEl.css("left").replace('px', ''));
    var myGuiderArrow = $guiderEl.find(".guider_arrow");
    var arrowElemLeft = parseInt(myGuiderArrow.css("left").replace('px', ''));
    $guiderEl.css("left", (guiderElemLeft + amount) + "px");
    myGuiderArrow.css("left", (arrowElemLeft - amount) + "px");
  },

  /**
   * Detect if a guider's element falls outside of the window and push it
   * in place if it does.
   *
   * This is meant to be bound to the guider element's 'guiders.show' event 
   */
  nudgeIntoWindow: function($guiderEl) {
    var windowWidth = $(window).width();
    var guiderOffset = $guiderEl.offset();
    var guiderElemWidth = $guiderEl.outerWidth();
    var isGuiderRight = (guiderOffset.left + guiderElemWidth > windowWidth);
    var isGuiderLeft = (guiderOffset.left < 0);
    // Check if the guider ends up to the left or to the right of the 
    // window and nudge it over until it fits
    if (isGuiderRight) {
      this.nudge($guiderEl, windowWidth - guiderOffset.left - guiderElemWidth);
    }
    if (isGuiderLeft) {
      this.nudge($guiderEl, 0 - guiderOffset.left);
    }
    // Unbind this event from the element
    $guiderEl.unbind("guiders.show");
  },

  /**
   * Checks if the tour should be shown
   */
  showTour: function() {
    if (_.isUndefined(guiders)) {
      return false;
    }

    if (this.options.forceTour) {
      return true;
    }
  
    if ($.cookie('storybase_show_builder_tour') === 'false') {
      return false;
    }

    return this.options.showTour;
  },

  show: function() {
    var that = this;

    var bindNudge = function(myGuider) {
      $(myGuider.elem).bind("guiders.show", function() {
        that.nudgeIntoWindow($(this));
      });
    }; 
    
    if (this.showTour()) { 
      guiders.createGuider({
        id: 'workflow-step-guider',
        attachTo: '#workflow-step #build',
        buttons: [
          {
            name: gettext("Next"),
            onclick: guiders.next
          }
        ],
        position: 6,
        title: gettext("Building a story takes five simple steps."),
        description: this.template['workflow-step-guider'](),
        next: 'section-list-guider',
        xButton: true,
        onShow: bindNudge 
      });
      guiders.createGuider({
        id: 'section-list-guider',
        attachTo: '#section-list',
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
        title: gettext("This is your table of contents."),
        // TODO: Remove reference to "Story Sections" tab
        description: gettext('This bar shows the sections in your story.'),
        prev: 'workflow-step-guider',
        next: 'section-thumbnail-guider',
        xButton: true,
        onShow: bindNudge
      });
      guiders.createGuider({
        id: 'section-thumbnail-guider',
        attachTo: '.section-thumbnail:first',
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
        title: gettext("Select the section you want to edit."),
        description: gettext("Click on a section to edit it. The section you are actively editing is highlighted."),
        prev: 'section-list-guider',
        next: 'section-manipulation-guider',
        xButton: true,
        onShow: bindNudge
      });
      guiders.createGuider({
        id: 'section-manipulation-guider',
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
        position: 6,
        title: gettext("You can also add, move or delete sections."),
        description: this.template['section-manipulation-guider'](),
        prev: 'section-thumbnail-guider',
        next: 'preview-guider',
        xButton: true,
        onShow: bindNudge
      });
      guiders.createGuider({
        id: 'preview-guider',
        attachTo: '#tools .preview',
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
        title: gettext("Preview your story at any time."),
        description: gettext("Clicking here lets you preview your story in a new window"),
        prev: 'section-manipulation-guider',
        next: 'exit-guider',
        xButton: true,
        onShow: bindNudge
      });
      guiders.createGuider({
        id: 'exit-guider',
        attachTo: '#tools .exit',
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
        title: gettext("You can leave your story at any time and come back later."),
        description: this.template['exit-guider'](),
        prev: 'preview-guider',
        next: 'help-guider',
        xButton: true,
        onShow: bindNudge
      });
      guiders.createGuider({
        attachTo: '#drawer-controls [title="Help"]',
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
        title: gettext("Get tips on how to make a great story."),
        description: gettext("Clicking the \"Help\" button shows you tips for the section you're currently editing. You can also click on the \"?\" icon next to an asset to find more help."),
        onShow: function(myGuider) {
          bindNudge(myGuider);
          that.dispatcher.trigger('do:show:help');
        },
        onHide: function(myGuider) {
          that.dispatcher.trigger('do:hide:help');
        },
        next: 'tooltip-guider',
        xButton: true
      });
      guiders.createGuider({
        attachTo: '#workflow-step #build',
        buttons: [
          {
            name: gettext("Prev"),
            onclick: guiders.prev
          },
          {
            name: gettext("Close"),
            onclick: guiders.hideAll
          }
        ],
        position: 6,
        offset: { left: 0, top: 20 },
        id: 'tooltip-guider',
        title: gettext("Need even more tips?"),
        description: gettext("You can find out more about many of the buttons and links by hovering over them with your mouse."),
        onShow: function(myGuider) {
          bindNudge(myGuider);
          $('#workflow-step #build').triggerHandler('mouseover');
        },
        onHide: function() {
          // Set a cookie so the user doesn't see the builder tour again
          $.cookie("storybase_show_builder_tour", false, {
            path: '/',
            // Don't show the tour for a very long time
            expires: 365
          });
          $('#workflow-step #build').triggerHandler('mouseout');
        },
        xButton: true
      });
      guiders.show('workflow-step-guider');
      // HACK: Workaround for #415.  In IE, re-nudge the first guider element
      // after waiting a little bit. In some cases, the initial CSS change 
      // above doesn't render properly. The pause seems to fix this.  Note
      // that this uses the internal guiders API to get the element.
      if (storybase.builder.views.MSIE) {
        setTimeout(function() {
          that.nudgeIntoWindow(guiders._guiderById('workflow-step-guider').elem);
        }, 200);
      }
    }
  }
});

storybase.builder.views.BuilderView = Backbone.View.extend({
  tagName: 'div',

  className: 'builder',

  options: {
    titleEl: '.story-title',
    visibleSteps: storybase.builder.views.VISIBLE_STEPS
  },

  initialize: function() {
    var that = this;
    var navViewOptions;
    var isNew = _.bind(function() {
      return !this.model.isNew();
    }, this)

    this.containerTemplates = this.options.containerTemplates;
    this.dispatcher = this.options.dispatcher;
    this.help = this.options.help;
    this._relatedStoriesSaved = false;
    this._tour = new storybase.builder.views.BuilderTour({
      dispatcher: this.dispatcher,
      forceTour: this.options.forceTour,
      showTour: this.options.showTour
    });

    if (_.isUndefined(this.model)) {
      // Create a new story model instance
      this.model = new storybase.models.Story({
        title: "",
        language: this.options.language
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
        className: 'next',
        title: gettext("Add Data to Your Story"),
        text: gettext("Next"),
        path: 'data/',
        enabled: isNew 
      });
    }
    else if (this.options.visibleSteps.publish) {
      navViewOptions.items.push({
        id: 'workflow-nav-publish-fwd',
        className: 'next',
        title: gettext("Publish My Story"),
        text: gettext("Next"),
        path: 'publish/',
        enabled: isNew,
        validate: this.options.visibleSteps.review ? true : this.simpleReview
      });
    }
    this.workflowNavView = new storybase.builder.views.WorkflowNavView(navViewOptions);

    if (this.options.showSectionList) {
      this.sectionListView = new storybase.builder.views.SectionListView({
        dispatcher: this.dispatcher,
        model: this.model
      });
    }
    this.unusedAssetView = new storybase.builder.views.UnusedAssetView({
      dispatcher: this.dispatcher,
      assets: this.model.unusedAssets
    });

    this._editViews = [];

    this.model.on("sync", this.triggerSaved, this);
    this.model.sections.on("reset", this.triggerReady, this);
    this.model.unusedAssets.on("sync reset add", this.hasAssetList, this);

    this.dispatcher.on("select:template", this.setStoryTemplate, this);
    this.dispatcher.on("do:save:story", this.save, this);
    this.dispatcher.on("add:sectionasset", this.showSaved, this);
    this.dispatcher.on("save:section", this.showSaved, this);
    this.dispatcher.on("save:story", this.showSaved, this);
    this.dispatcher.on("ready:story", this.createEditViews, this);
    this.dispatcher.on("save:story", this.setTitle, this);
    this.dispatcher.on("ready:story", this.setTitle, this);
    this.dispatcher.on("created:section", this.handleCreateSection, this);

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
      //this.dispatcher.trigger('select:section', 'story-info');
      this.dispatcher.trigger('select:section', this._editViews[0].getSection());
    }
  },

  render: function() {
    console.info('Rendering builder view');
    var that = this;
    this.$el.prepend(this.unusedAssetView.render().$el.hide());
    if (this.sectionListView) {
      this.sectionListView.render();
    }
    if (this.workflowNavView) {
      this.workflowNavView.render();
    }
    this.renderEditViews();
    return this;
  },

  getWorkflowNavView: function() {
    return this.workflowNavView;
  },

  getSubNavView: function() {
    if (this.sectionListView) {
      return this.sectionListView;
    }
    else {
      return null;
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
    if (this.sectionListView) {
      this.sectionListView.setWidth();
    }

    // Show the tour
    this._tour.show();

    this.dispatcher.trigger("register:drawerview", this.unusedAssetView);
  },

  onHide: function() {
    this.dispatcher.trigger("unregister:drawerview", this.unusedAssetView);
  },

  workflowNavView: function() {
    if (this.sectionListView) {
      return this.sectionListView;
    }
    else {
      return this.workflowNavView;
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
    this.model.fromTemplate(this.templateStory, {
      language: this.options.language
    });
    this.dispatcher.trigger("ready:story", this.model);
  },

  save: function() {
    console.info("Saving story");
    var that = this;
    var isNew = this.model.isNew();
    this.model.save(null, {
      success: function(model, response) {
        that.dispatcher.trigger('save:story', model);
        model.saveSections();
        if (!that._relatedStoriesSaved) {
          model.saveRelatedStories();
        }
        if (isNew) {
          that.dispatcher.trigger('navigate', model.id + '/', {
            trigger: true 
          });
          // Re-render the navigation view to enable the button
          if (that.navView) {
            that.navView.render();
          }
        }
      }
    });
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
      document.title =  this.options.siteName + " | " + title;
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
  }
});

storybase.builder.views.LastSavedView = Backbone.View.extend({
  tagName: 'div',

  id: 'last-saved',

  options: {
    textId: 'last-saved-text',
    buttonId: 'save-button'
  },

  events: function() {
    var events = {};
    events['click #' + this.options.buttonId] = 'handleClick';
    return events;
  },

  /**
   * Make an ISO-8601 formatted string adhere to the 'strict' standard.
   *
   * In our case, this just means removing the microseconds from the 
   * string.
   */
  _makeStrict: function(dateStr) {
    var re = /\.\d+/;

    return dateStr.replace(re, "");
  },

  /**
   * Convert an ISO-8601 formatted date string into a Date object.
   *
   * Takes into account minor browser differences.
   */
  parseDate: function(date) {
    var parsedDate;

    if (_.isDate(date)) {
      // If the argument is already a date object, just return it
      return date;
    }

    // Otherwise, it's a string and we need to make a Date object out of it
    parsedDate = new Date(date);
    if (!isNaN(parsedDate.getTime())) {
      // We successfully parsed the date string. Return the Date object
      return parsedDate;
    }

    // The date wasn't successfully parsed, this is likely because the browser
    // doesn't support microseconds in the ISO-8601 datestring as returned
    // by the API (IE).
    return new Date(this._makeStrict(date));
  },

  initialize: function() {
    this.lastSaved = !!this.options.lastSaved ? this.parseDate(this.options.lastSaved) : null;

    this.dispatcher = this.options.dispatcher;
    this.dispatcher.on('save:section', this.updateLastSaved, this);
    this.dispatcher.on('save:story', this.updateLastSaved, this);
    this.dispatcher.on('ready:story', this.showButton, this);

    this.$textEl = $("<span></span>").attr('id', this.options.textId).appendTo(this.$el);
    this.$buttonEl = $('<button type="button">' + gettext("Save") + '</button>')
      .attr('id', this.options.buttonId)
      .attr('title', gettext("Click to save your story"))
      .hide()
      .appendTo(this.$el);
      if (jQuery().tooltipster) {
        this.$buttonEl.tooltipster();
      }
  },

  updateLastSaved: function() {
    var that = this;
    this.lastSaved = new Date(); 
    this.render();
    this.showText();
    this.$textEl.fadeOut(20000, function() {
      that.showButton();
    });
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

  showButton: function() {
    this.$textEl.hide();
    this.$buttonEl.show();
    return this;
  },

  showText: function() {
    this.$textEl.show();
    this.$buttonEl.hide();
    return this;
  },

  handleClick: function(evt) {
    this.dispatcher.trigger('do:save:story');
  },

  render: function() {
    var lastSavedStr;
    if (this.lastSaved) {
      lastSavedStr = gettext('Last Saved') + ' ' + this.formatDate(this.lastSaved);
      this.$textEl.html(lastSavedStr);
      this.$buttonEl.attr('title', lastSavedStr);
    }
    return this;
  }
});

storybase.builder.views.UnusedAssetDrawerMixin = {
  drawerButton: function() {
    if (_.isUndefined(this.drawerButtonView)) {
      this.drawerButtonView = new storybase.builder.views.DrawerButtonView({
        dispatcher: this.dispatcher,
        buttonId: 'unused-assets',
        text: gettext('Assets'),
        title: gettext("Show a list of assets you removed from your story"),
        parent: this
      });
    }
    return this.drawerButtonView;
  },

  drawerOpenEvents: 'do:show:assetlist',

  drawerCloseEvents: 'do:hide:assetlist',

  // Workaround for issue where draggable element is hidden when its
  // container element has an overflow property that is not visible
  extraEvents: {
    'start:drag:asset': function() {
      this.$el.addClass('dragging');
    },

    'stop:drag:asset': function() {
      this.$el.removeClass('dragging');
    },
  }
};

/** 
 * A list of assets associated with the story but not used in any section.
 */
storybase.builder.views.UnusedAssetView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.UnusedAssetDrawerMixin, {
    tagName: 'div',

    id: 'unused-assets',

    templateSource: $('#unused-assets-template').html(),

    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      this.template = Handlebars.compile(this.templateSource);
      this.assets = this.options.assets;

      // When the assets are synced with the server, re-render this view
      this.assets.on("add reset sync remove", this.render, this);
      // When an asset is removed from a section, add it to this view
      this.dispatcher.on("remove:sectionasset", this.addAsset, this);
      this.dispatcher.on("do:show:assetlist", this.show, this);
      this.dispatcher.on("do:hide:assetlist", this.hide, this);
      this.assets.on("remove", this.handleRemove, this);
    },

    render: function() {
      var that = this;
      var assetsJSON = this.assets.toJSON();
      // Pluck specific attributes from the asset. This simplifies the
      // logic in the template
      assetsJSON = _.map(assetsJSON, function(assetJSON) {
        var attrs = {
          asset_id: assetJSON.asset_id,
          type: assetJSON.type
        };
        if (assetJSON.thumbnail_url) {
          attrs.thumbnail_url = assetJSON.thumbnail_url;
        }
        else if (assetJSON.body) {
          attrs.body = assetJSON.body;
        }

        if (assetJSON.url) {
          attrs.url = assetJSON.url;
        }
        return attrs;
      });
      var context = {
        assets: assetsJSON
      };
      this.$el.html(this.template(context));
      this.$('.unused-asset').draggable({
        revert: 'invalid',
      // Workaround for issue where draggable element is hidden when its
      // container element has an overflow property that is not visible
        start: function() {
          that.dispatcher.trigger("start:drag:asset")
        },
        stop: function() {
          that.dispatcher.trigger("stop:drag:asset")
        }
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
    },

    show: function() {
      return this.$el.show();
    },

    hide: function() {
      return this.$el.hide();
    }
  })
);

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
    var settings;

    if (file) {
      formData = new FormData;
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
    else {
      // A file object was not available, likely because the browser doesn't
      // support the File API.  Try uploading via an IFRAME
      if (options.form) {
        this.uploadFileIframe(model, options.form, url, options); 
      }
    }
  },

  uploadFileIframe: function(model, form, url, options) {
    // Get a jQuery object for the form 
    var $form = $(form);
    var timeout = 250;
    var loadHandler = function(evt) {
      var iframe = evt.target; 
      var content;

      if (iframe.detachEvent) {
        iframe.detachEvent("onload", loadHandler);
      }
      else {
        iframe.removeEventListener("load", loadHandler);
      }

      if (iframe.contentDocument) {
        content = iframe.contentDocument.body.innerHTML;
      }
      else if (iframe.contentWindow) {
        content = iframe.contentWindow.document.body.innerHTML;
      }
      else if (iframe.document) {
        content = iframe.document.body.innerHTML;
      }
      model.fetch({
        success: function(model, response) {
          if (options.success) {
            options.success(model, response);
          }
        }
      });
      setTimeout(function() {
        iframe.parentNode.removeChild(iframe);
      }, timeout);
    };
    // Create a hidden iframe and append it to the DOM
    // We append it to the body rather than the form's parent element because
    // the form's parent element gets removed before the form can post
    var iframe = document.createElement('iframe');
    iframe.setAttribute('id', 'storybase-upload-iframe');
    iframe.setAttribute('name', 'storybase-upload-iframe');
    iframe.setAttribute('width', '0');
    iframe.setAttribute('height', '0');
    iframe.setAttribute('border', '0');
    iframe.setAttribute('style', "width: 0; height: 0; border: none;");
    document.body.appendChild(iframe);
    window.frames['storybase-upload-iframe'].name = 'storybase-upload-iframe';

    if (iframe.addEventListener) {
      iframe.addEventListener('load', loadHandler, true);
    }
    if (iframe.attachEvent) {
      iframe.attachEvent('onload', loadHandler);
    }

    $form.attr('target', 'storybase-upload-iframe');
    $form.attr('action', url);
    $form.attr('method', 'POST');
    $form.attr('enctype', "multipart/form-data");
    $form.attr('encoding', "multipart/form-data");
 
    form.submit();
  }
};


/**
 * Mixin for views that have a navigation subview
 */
storybase.builder.views.NavViewMixin = {
  getWorkflowNavView: function() {
    return this.workflowNavView;
  }
};

// TODO: Remove this view
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
    'click .spacer': 'clickAddSection',
    'sortupdate': 'handleSort',
    'mousedown .scroll-right': 'scrollRight',
    'mousedown .scroll-left': 'scrollLeft',
    'mouseup': 'stopScroll',
  },

  initialize: function() {
    this.dispatcher = this.options.dispatcher;
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
      title: gettext("Story Information"),
      tooltip: gettext("This section has basic information people will see when browsing stories on the site"),
      pseudoSectionId: 'story-info'
    });
    this._sortedThumbnailViews.push(view);
    this._thumbnailViews[view.pseudoSectionId] = view;
  },

  addCallToActionThumbnail: function() {
    var view = new storybase.builder.views.PseudoSectionThumbnailView({
      dispatcher: this.dispatcher,
      title: gettext("Call to Action"),
      tooltip: gettext("Inspire your readers to act after they read your story"),
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
  clickAddSection: function(evt) {
    evt.stopPropagation(); 
    evt.preventDefault();
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
      template_section: this.model.sections.at(0).get('template_section'),
      language: this.options.language
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
      // Add tooltip for section adding icon
      if (jQuery().tooltipster) {
        this.$('.tooltip').tooltipster({
          position: 'top'
        });
      }
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
        title: this.title,
        tooltip: this.options.tooltip
      };
      this.$el.html(this.template(context));
      if (this.options.tooltip && jQuery().tooltipster) {
        this.$('.section-thumbnail').tooltipster({
          position: 'bottom'
        });
      }
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

    initialize: function() {
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
        //this.dispatcher.trigger('do:show:help', this.help.toJSON()); 
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
    },

    getSection: function() {
      return this.pseudoSectionId;
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
    events['change ' + this.options.titleEl] = 'change';
    events['change ' + this.options.bylineEl] = 'change';
    return events;
  },

  options: {
    titleEl: '[name="title"]',
    bylineEl: '[name="byline"]',
    summaryEl: 'textarea[name="summary"]' 
  },

  render: function() {
    var that = this;
    var handleChange = function () {
      // Trigger the change event on the underlying element 
      that.$(that.options.summaryEl).trigger('change');
    };
    this.$el.html(this.template(this.model.toJSON()));
    // Initialize wysihmtl5 editor
    this.summaryEditor = this.getEditor(
      this.$(this.options.summaryEl)[0],
      {
        change: handleChange
      }
    );
      
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

    options: {
      titleEl: '[name="title"]',
      bylineEl: '[name="byline"]'
    },

    events: function() {
      var events = {};
      events['change ' + this.options.titleEl] = 'change';
      events['change ' + this.options.bylineEl] = 'change';
      return events;
    },

    initialize: function() {
      this.template = Handlebars.compile(this.templateSource);
      this.dispatcher = this.options.dispatcher;
    },

    render: function() {
      var that = this;
      var context = this.model.toJSON();
      context.prompt = this.options.prompt;
      this.$el.html(this.template(context));
        
      this.delegateEvents(); 
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
 * View for editing the story's call to action 
 */
storybase.builder.views.CallToActionEditView = storybase.builder.views.PseudoSectionEditView.extend({ 
  className: 'edit-call-to-action edit-section',

  // The section edit views can be identified by the ID of their
  // sections, but these pseudo-section edit views need an
  // explicit identifier
  pseudoSectionId: 'call-to-action',

  options: {
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

  options: {
    containerEl: '.storybase-container-placeholder',
    titleEl: '.section-title',
    selectLayoutEl: 'select.layout'
  },

  events: function() {
    var events = {};
    events['change ' + this.options.selectLayoutEl] = 'change';
    events['change ' + this.options.titleEl] = 'change';
    return events;
  },

  initialize: function() {
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
        selected: that.model.get('layout') == layout.layout_id,
        slug: layout.slug
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
    // Turn the basic select element into a fancy graphical selection
    // widget
    this.$el.find(this.options.selectLayoutEl).graphicSelect();
    // Delegate events so our event bindings work after we've removed
    // this element from the DOM
    this.delegateEvents();
    this.applyPolyfills();
    return this;
  },

  show: function(section) {
    section = _.isUndefined(section) ? this.model : section;
    var help = this.model.get('help') || this.defaultHelp.toJSON();
    if (section == this.model) {
      console.debug('showing section ' + section.get('title'));
      this.$el.show();
      // For now, don't show help automatically
      //this.dispatcher.trigger('do:show:help', help); 
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
  },

  getSection: function() {
    return this.model;
  },
  
  /**
   * Apply any available polyfills.
   *
   */
  applyPolyfills: function() {
    if (!Modernizr.input.placeholder) {
      window.polyfills.placeholders();
    }
  }
});

storybase.builder.views.SectionAssetEditView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.FileUploadMixin, 
           storybase.builder.views.RichTextEditorMixin, {
    tagName: 'div',

    className: 'edit-section-asset',

    options: {
      wrapperEl: '.wrapper',
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

    events: {
      "click .asset-type": "selectType", 
      "click .remove": "remove",
      "click .edit": "edit",
      "click .help": "showHelp",
      'click input[type="reset"]': "cancel",
      'submit form.bbf-form': 'processForm',
      'drop': 'handleDrop'
    },

    states: ['select', 'display', 'edit'],

    initialize: function() {
      console.debug("Initializing new section asset edit view");
      this.modelOptions = {
        language: this.options.language
      }
      var modelOptions = _.extend({}, this.modelOptions);
      this.container = this.options.container;
      this.dispatcher = this.options.dispatcher;
      this.assetTypes = this.options.assetTypes;
      this.section = this.options.section;
      this.story = this.options.story;
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
          placeholder: gettext("Click to edit caption"),
          height: '2.8em'
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
      var storyLicense = this.story.get('license');
      if (isNew && _.isUndefined(attributes['license']) && storyLicense) {
        // If this is the initial save and the story has a license
        // defined and the asset has no explicit license defined, set the
        // asset license to that of the story.
        attributes['license'] = storyLicense;
      }
      this.model.save(attributes, {
        success: function(model) {
          // When uploading files, we'll let the upload handler re-render
          // This is mostly because we need to keep the form element for
          // IFRAME-based uploads
          if (!options.deferRender) {
            that.setState('display');
            that.render();
          }
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
          // We were able to retrieve the file via the File API
          file = data.image;
        }

        if (!data.url) {
          // Set a callback for saving the model that will upload the
          // image.
          options.deferRender = true;
          options.success = function(model) {
            that.uploadFile(model, 'image', file, {
              form: e.target, 
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
      this.model = new storybase.models.Asset(this.modelOptions);
      // Listen to events on the new model
      this.bindModelEvents();
      this.setState('select').render();
    },

    assetTypeHelp: {
      image: Handlebars.compile($('#image-help-template').html()),
      text: Handlebars.compile($('#text-help-template').html()), 
      video: Handlebars.compile($('#video-help-template').html())
    },

    getAssetTypeHelp: function(type) {
      var help = this.assetTypeHelp[type]; 
      if (_.isFunction(help)) {
        help = help();
      }
      else {
        help = gettext("There isn't help for this type of asset yet, or you haven't selected an asset type.");
      }
      return help;
    },

    /**
     * Show help 
     */
    showHelp: function(evt) {
      var help = _.extend({
        title: "",
        body: ""
      }, this.options.help);
      var assetHelp = this.getAssetTypeHelp(this.model.get('type'));
      help.body += assetHelp;
      this.dispatcher.trigger('do:show:help', help);
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
    className: 'view-container',

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

      this.workflowNavView = new storybase.builder.views.WorkflowNavView({
        model: this.model,
        dispatcher: this.dispatcher,
        items: [
          {
            id: 'workflow-nav-build-back',
            className: 'prev',
            title: gettext("Continue Writing Story"),
            text: gettext("Previous"),
            path: ''
          },
          {
            id: 'workflow-nav-tag-fwd',
            className: 'next',
            title: gettext("Tag"),
            text: gettext("Next"),
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
        this.workflowNavView.render();
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
        this.addDataSet(formData, evt.target);
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

    addDataSet: function(attrs, form) {
      var that = this;
      var file = null;
      if (attrs.file) {
        file = attrs.file;
        delete attrs.file;
      }
      this.collection.create(attrs, {
        success: function(model, response) {
          that.trigger('save:dataset', model);
          if (file || !attrs.url) {
            that.uploadFile(model, 'file', file, {
              form: form,
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
    className: 'view-container',

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
      this.workflowNavView = new storybase.builder.views.WorkflowNavView({
        model: this.model,
        dispatcher: this.dispatcher,
        items: [
          {
            id: 'workflow-nav-tag-back',
            className: 'prev',
            title: gettext("Back to Tag"),
            text: gettext("Previous"),
            path: 'tag/'
          },
          {
            id: 'workflow-nav-publish-fwd',
            className: 'next',
            title: gettext("Publish My Story"),
            text: gettext("Next"),
            path: 'publish/'
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
      this.workflowNavView.render();
      this.delegateEvents();
      return this;
    },

    previewStory: function(evt) {
      evt.preventDefault();
      var url = '/stories/' + this.model.id + '/viewer/';
      this.previewed = true;
      // Re-render the nav view to reflect the newly enabled button
      this.workflowNavView.render();
      window.open(url);
    },

    hasPreviewed: function() {
      return this.previewed;
    }
  })
);

storybase.builder.views.TaxonomyView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.NavViewMixin, {
    id: 'share-taxonomy',

    className: 'view-container',

    templateSource: $('#share-taxonomy-template').html(),

    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      this.template = Handlebars.compile(this.templateSource);
      this.workflowNavView = new storybase.builder.views.WorkflowNavView({
        model: this.model,
        dispatcher: this.dispatcher,
        items: [
          {
            id: 'workflow-nav-data-back',
            className: 'prev',
            title: gettext("Back to Add Data"),
            text: gettext("Previous"),
            path: 'data/'
          },
          {
            id: 'workflow-nav-review-fwd',
            className: 'next',
            title: gettext("Review"),
            text: gettext("Next"),
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
      this.workflowNavView.render();

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


storybase.builder.views.LegalView = Backbone.View.extend({
  id: 'share-legal',

  templateSource: $('#share-legal-template').html(),

  events: {
    'change input[name=license]': 'changeLicenseAgreement',
    'click .view-agreement': 'showForm',
    'submit form': 'processForm'
  },

  options: {
    'title': gettext("Accept the legal agreement")
  },

  // Schema for form
  schema: function () {
    var isChecked = storybase.forms.isChecked;
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
      }
    };
  },

  initialize: function() {
    var formVals = {
      permission: this.hasPermission,
      license: this.agreedLicense
    };
    this.dispatcher = this.options.dispatcher;
    this.template = Handlebars.compile(this.templateSource);
    this.hasPermission = this.model && this.model.get('status') === 'published';
    this.agreedLicense = this.model && this.model.get('status') === 'published';
    this.form = new Backbone.Form({
      schema: this.schema(),
      data: formVals
    });
    if (_.isUndefined(this.model)) {
      this.dispatcher.on("ready:story", this.setStory, this);
    }
  },

  setStory: function(story) {
    this.model = story;
  },

  validate: function() {
    var formValues = this.form.getValue();
    var errors = this.form.validate();
    if (!errors) {
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
      this.render();
      this.dispatcher.trigger("accept:legal");
    }
  },

  // TODO: Remove this if it's really not needed
  /*
  setRadioEnabled: function() {
    this.form.fields['commercial'].$('input').prop('disabled', !this.agreedLicense);
    this.form.fields['derivatives'].$('input').prop('disabled', !this.agreedLicense);
  },
  */

  /**
   * Workaround for limitations of form initial value setting.
   */
  updateFormDefaults: function() {
    // HACK: Work around weird setValue implementation for checkbox
    // type.  Maybe make a custom editor that does it right.
    this.form.fields.permission.editor.$('input[type=checkbox]').prop('checked', this.hasPermission);
    this.form.fields.license.$('input[type=checkbox]').prop('checked', this.agreedLicense);
    // TODO: Remove this if not needed
    //this.setRadioEnabled();
  },

  render: function(options) {
    options = options || {};
    var showForm = !(this.hasPermission && this.agreedLicense) || options.showForm;
    this.$el.html(this.template({
      title: this.options.title,
      showForm: showForm 
    }));
    if (showForm) {
      this.form.render().$el.append('<input type="submit" value="' + gettext("Agree") + '" />');
      this.updateFormDefaults();
      this.$el.append(this.form.el);
    }
    this.delegateEvents();

    return this;
  },

  changeLicenseAgreement: function(evt) {
    this.agreedLicense = $(evt.target).prop('checked');
    // TODO: Remove this if not needed
    //this.setRadioEnabled();
  },

  completed: function() {
    return this.agreedLicense && this.hasPermission;
  },

  showForm: function() {
    return this.render({showForm: true});
  }
});

storybase.builder.views.LicenseDisplayView = Backbone.View.extend({
  id: 'cc-license',

  initialize: function() {
    var license = _.isUndefined(this.model) ? null : this.model.get('license');
    this.dispatcher = this.options.dispatcher;
    this._licenseHtml = null;
    if (_.isUndefined(this.model)) {
      this.dispatcher.on("ready:story", this.setStory, this);
    }
    this.dispatcher.on("select:license", this.getLicenseHtml, this);
    if (license) {
      this.getLicenseHtml();
    }
  },

  setStory: function(story) {
    this.model = story;
  },

  getLicenseHtml: function() {
    var that = this;
    var license = this.model.get('license');
    var params = storybase.utils.licenseStrToParams(license);
    // Set provision license text just so the user sees something
    this._licenseHtml = "<p>" + gettext("You selected the ") + license + " " + gettext("license.") + "</p>";
    this.render();
    // Now try to get the license from the (proxied) Creative Commons
    // endpoint.  If this succeeds, we'll re-render when we're finished
    $.get(this.options.licenseEndpoint, params, function(data) {
      // The endpoint returns XML. Use jQuery to grab the 'html' element
      // of the XML response and the convert the element contents to 
      // a string.
      // 
      // If we just append the matching elements, it doesn't display
      // correctly in the browser
      that._licenseHtml = $('<div>').append($(data).find("html").contents()).clone().html();
      that.render();
    });
  },

  render: function() {
    this.$el.html(this._licenseHtml);
  }
});

storybase.builder.views.LicenseView = Backbone.View.extend({
  id: 'share-license',

  events: {
    'submit form': 'processForm',
    'click .change-license': 'showForm'
  },

  options: {
    title: gettext("Select a license"),
    templateSource: $('#share-license-template').html()
  },

  schema: function() {
    return {
      'commercial': {
        type: 'Radio',
        title: '',
        options: Handlebars.compile($('#share-cc-commercial-template').html())(),
        validators: ['required']
      },
      'derivatives': {
        type: 'Radio',
        title: '',
        options: Handlebars.compile($('#share-cc-derivatives-template').html())(),
        validators: ['required']
      }
    };
  },
 
  setStory: function(story) {
    this.model = story;
  },

  initialize: function() {
    var license = this.model ? this.model.get('license') : null;
    var formVals = storybase.utils.licenseStrToParams(license);
    this.dispatcher = this.options.dispatcher;
    this.form = new Backbone.Form({
      schema: this.schema(),
      data: formVals
    });
    this.licenseDisplayView = new storybase.builder.views.LicenseDisplayView({
      dispatcher: this.dispatcher,
      model: this.model,
      licenseEndpoint: this.options.licenseEndpoint
    });
    this.template = Handlebars.compile(this.options.templateSource);
    if (_.isUndefined(this.model)) {
      this.dispatcher.on("ready:story", this.setStory, this);
    }
  },

  completed: function() {
    return this.model && this.model.get('license');
  },

  setLicense: function(params) {
    this.model.set('license', storybase.utils.licenseParamsToStr(params));
    this.model.save();
  },

  validate: function() {
    var formValues = this.form.getValue();
    var errors = this.form.validate();
    if (!errors) {
      this.setLicense(formValues);
      return true;
    }
    else {
      return false;
    }
  },

  processForm: function(evt) {
    evt.preventDefault();
    if (this.validate()) {
      this.dispatcher.trigger("select:license");
      // Update the form data to the new value of the form, otherwise
      // the new values will get clobbered when the form is re-rendered
      // in render()
      this.form.data = this.form.getValue();
      this.render();
    }
  },

  render: function(options) {
    options = options || {};
    var license = this.model.get('license');
    var showForm = (license ? false : true) || options.showForm;
    this.$el.html(this.template({
      title: this.options.title,
      license: license,
      showForm: showForm
    }));
    if (showForm) {
      this.form.render().$el.append('<input type="submit" value="' + gettext("Select License") + '" />');
      this.$el.append(this.form.el);
    }
    else {
      this.licenseDisplayView.setElement(this.$('#cc-license')).render();
    }
    this.delegateEvents();

    return this;
  },

  showForm: function() {
    return this.render({showForm: true});
  }
});

storybase.builder.views.PublishView = Backbone.View.extend(
  _.extend({}, storybase.builder.views.NavViewMixin, {
    id: 'share-publish',

    className: 'view-container',

    events: {
      'click .publish': 'handlePublish',
      'click .unpublish': 'handleUnpublish',
      'click a.popup': 'handleView'
    },

    options: {
      // Source of template for the main view layout
      templateSource: $('#share-publish-template').html(),
      // Source of the template with markup/text that is displayed
      // when all the required steps have been completed.
      readyTemplateSource: $('#publish-ready-msg-template').html(),
      // Source of the template with markup/text that is displayed
      // when the story has been published
      publishedTemplateSource: $('#publish-published-msg-template').html(),
      // Selector for the element (defined in templateSource) that
      // shows the remaining publication steps
      todoEl: '.publish-todo',
      // Selector for the element (defined in templateSource) that
      // shows the sharing widgets
      sharingEl: '.publish-sharing',
      // Selector for the element (defined in templateSource) that 
      // contains the subviews
      subviewEl: '.left'
    },

    initialize: function() {
      var navViewOptions;
  
      this.dispatcher = this.options.dispatcher;
      this.template = Handlebars.compile(this.options.templateSource);
      this.readyTemplate = Handlebars.compile(this.options.readyTemplateSource);
      this.publishedTemplate = Handlebars.compile(this.options.publishedTemplateSource);
      this.acceptedLegal = _.isUndefined(this.model) ? false : this.model.get('status') === "published";
      this.legalView = new storybase.builder.views.LegalView({
        model: this.model,
        dispatcher: this.dispatcher
      });
      this.licenseView = new storybase.builder.views.LicenseView({
        model: this.model,
        dispatcher: this.dispatcher,
        licenseEndpoint: this.options.licenseEndpoint
      });
      this.featuredAssetView = new storybase.builder.views.FeaturedAssetView({
        dispatcher: this.dispatcher,
        language: this.options.language,
        story: this.model
      });
      this.subviews = [this.legalView, this.licenseView, this.featuredAssetView];
      this.updateTodo(null, false);

      navViewOptions = {
        model: this.model,
        dispatcher: this.dispatcher,
        items: []
      };
      if (this.options.visibleSteps.review) {
        navViewOptions.items.push({
          id: 'workflow-nav-build-back',
          className: 'prev',
          title: gettext("Back to Review"),
          text: gettext("Previous"), 
          path: 'review/'
        });
      }
      else {
        navViewOptions.items.push({
          id: 'workflow-nav-review-back',
          className: 'prev',
          title: gettext("Continue Writing Story"),
          text: gettext("Previous"),
          path: ''
        });
      }
      this.workflowNavView = new storybase.builder.views.WorkflowNavView(navViewOptions);
      
      if (_.isUndefined(this.model)) {
        this.dispatcher.on("ready:story", this.setStory, this);
      }
      this.dispatcher.on("accept:legal", this.handleAcceptLegal, this);
      this.dispatcher.on("select:license", this.updateTodo, this);
      this.dispatcher.on("select:featuredasset", this.updateTodo, this);
    },

    todoItemLink: function(view) {
      return '<a href="#' + view.$el.attr('id') + '" class="publish-todo-item">' + view.options.title + '</a>';
    },

    updateTodo: function(obj, render) {
      render = _.isUndefined(render) ? true : render;
      this.todo = [];
  
      _.each(this.subviews, function(view) {
        if (!view.completed()) {
          this.todo.push(this.todoItemLink(view));
        }
      }, this);

      if (render) {
        this.render({replace: false});
      }
      return this;
    },

    setStory: function(story) {
      this.model = story;
    },

    /**
     * Callback for when legal agreement is accepted.
     */
    handleAcceptLegal: function() {
      this.acceptedLegal = true;
      this.updateTodo(null, true);
    },


    handlePublish: function(evt) {
      var that = this;
      var triggerPublished = function(model, response) {
        that.dispatcher.trigger('publish:story', model);
        that.dispatcher.trigger('alert', 'success', 'Story published');
        that.render({replace: false});
      };
      var triggerError = function(model, response) {
        that.dispatcher.trigger('error', "Error publishing story");
      };
      this.model.save({'status': 'published'}, {
        success: triggerPublished, 
        error: triggerError 
      });
      evt.preventDefault();
    },

    handleUnpublish: function(evt) {
      evt.preventDefault();
      var that = this;
      var success = function(model, response) {
        that.dispatcher.trigger('alert', 'success', 'Story unpublished');
        that.render({replace: false});
      };
      var triggerError = function(model, response) {
        that.dispatcher.trigger('error', "Error unpublishing story");
      };
      this.model.save({'status': 'draft'}, {
        success: success, 
        error: triggerError 
      });
    },

    handleView: function(evt) {
      var url = $(evt.target).attr('href');
      window.open(url);
      evt.preventDefault();
    },

    getStoryUrl: function() {
      var url = this.model ? this.model.get('url') : '';
      var loc = window.location;
      if (url) {
        url = loc.protocol + "//" + loc.host + url;
      }
      return url;
    },

    storyPublished: function() {
      return this.model ? (this.model.get('status') === "published") : false;
    },

    renderButtons: function() {
      var $publishBtn = this.$('.publish');
      var $viewBtn = this.$('.view-story');
      var $unpublishBtn = this.$('.unpublish');

      if (this.storyPublished()) {
        $publishBtn.hide();
        $viewBtn.show();
        $unpublishBtn.show();
      }
      else {
        if (this.todo.length) {
          $publishBtn.attr('disabled', 'disabled');
        }
        else {
          $publishBtn.attr('disabled', null);
        }
        $publishBtn.show();
        $viewBtn.hide();
        $unpublishBtn.hide();
      }
    },

    renderTodo: function() {
      var $el = this.$(this.options.todoEl);
      var html;
      
      if (this.todo.length) {
        html = gettext("You need to ") + this.todo.join(", ");
      }
      else {
        if (this.storyPublished()) {
          html = this.publishedTemplate();
        }
        else {
          html = this.readyTemplate(); 
        }
      }
      $el.html(html);
    },

    renderSharing: function() {
      var $el = this.$(this.options.sharingEl);
      if (this.storyPublished()) {
        $el.show();
      }
      else {
        $el.hide();
      }
    },

    render: function(options) {
      options = options || {replace: true};
      var context = {
        url: this.getStoryUrl(),
        title: this.model.get('title'),
        showSharing: this.options.showSharing
      };
      if (options.replace) {
        this.$el.html(this.template(context));
        _.each(this.subviews, function(view) {
          this.$(this.options.subviewEl).append(view.render().el);
        }, this);
      }
      this.renderTodo();
      this.renderButtons();
      if (this.options.showSharing) {
        this.renderSharing();
      }
      if (window.addthis) {
        // Render the addthis toolbox.  We have to do this explictly
        // since it wasn't in the DOM when the page was loaded.
        addthis.toolbox(this.$('.addthis_toolbox')[0], {
          // Don't append clickback URL fragment so users get a clean
          // URL when clicking the permalink button
          data_track_clickback: false
        });
      }
      this.workflowNavView.render();
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

    options: {
      title: gettext("Select a featured image"),
      templateSource: $('#featured-asset-template').html(),
    },

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
      this.template = Handlebars.compile(this.options.templateSource);
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

    completed: function() {
      return !_.isUndefined(this.model);
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
      if (this._state === 'add' && !this.form.model.isNew()) {
        this.form.model = new storybase.models.Asset({
          language: this.options.language,
          type: 'image'
        });
      }
      return this;
    },

    getForm: function() {
      var form = new Backbone.Form({
        model: new storybase.models.Asset({
          language: this.options.language,
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
      var context = {
        title: this.options.title
      };
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
      var form = e.target;
      var errors = this.form.validate();
      var file;
      var url;
      var options = {};
      var that = this;
      if (!errors) {
        this.form.commit();
        file = this.form.model.get('image');
        url =  this.form.model.get('url');
        if (file || !url) {
          // Don't re-render until after the upload has finished
          options.deferRender = true;
          // Set a callback for saving the model that will upload the
          // image.
          options.success = function(model) {
            that.uploadFile(model, 'image', file, {
              form: form,
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
      model.set('license', this.story.get('license'));
      model.save(null, {
        success: function(model) {
          that.model = model;
          if (!options.deferRender) {
            that.setState('display');
            that.render();
          }
          that.story.assets.add(model);
          that.story.setFeaturedAsset(model);
          that.dispatcher.trigger('select:featuredasset', model);
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
      this.dispatcher.trigger('select:featuredasset', this.model);
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
