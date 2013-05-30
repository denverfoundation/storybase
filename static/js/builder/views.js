;(function($, _, Backbone, storybase) {
  var Builder = storybase.builder;
  if (_.isUndefined(Builder.views)) {
    Builder.views = {};
  }
  var Views = Builder.views;

  var Asset = storybase.models.Asset;
  var DataSet = storybase.models.DataSet;
  var DataSets = storybase.collections.DataSets;
  var FeaturedAssets = storybase.collections.FeaturedAssets;
  var Locations = storybase.collections.Locations;
  var Section = storybase.models.Section;
  var Story = storybase.models.Story;
  var Tags = storybase.collections.Tags;
  var capfirst = storybase.utils.capfirst;
  var geocode = storybase.utils.geocode;
  var hasAnalytics = storybase.utils.hasAnalytics;
  var licenseParamsToStr = storybase.utils.licenseParamsToStr;
  var licenseStrToParams = storybase.utils.licenseStrToParams;
  var prettyDate = storybase.utils.prettyDate;
  var HandlebarsTemplateMixin = storybase.views.HandlebarsTemplateMixin;
  var HandlebarsTemplateView = storybase.views.HandlebarsTemplateView;


  /**
   * Default visible steps of the story builder workflow.  
   *
   * These are usually passed to AppView when it is initialized.  However,
   * these defaults are provided to better document the behavior of the
   * app and for testing independent of the server-side code.
   */
  var VISIBLE_STEPS = {
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
  var MSIE = ($.browser !== undefined) && ($.browser.msie === true);

  /**
   * A section has been successfully saved
   *
   * @event save:section
   * @param Section section Section that was saved
   *     been saved.
   * @param Boolean [showAlert] Should an alert be displayed by a callback 
   *     bound to this event.
   */

  /**
   * A story has been successfully saved
   *
   * @event save:story
   * @param {Story} story Story model instance that was successfully
   *     saved.
   * @param {Boolean} [showAlert] Should an alert be displayed by a callback 
   *     bound to this event.
   */

  /**
   * Set the help item to be displayed in the help view.
   *
   * @event do:set:help
   * @param {object} help Representation of help to be displayed in the
   *   help view in the drawer.  This object should at least have a title
   *   and body property.
   */

  /**
   * Remove all help items from the help view.
   *
   * @event do:clear:help
   */

  /**
   * Set the view that defines action buttons that appear at the top of
   * the help content in the drawer.
   *
   * Currently, this is just used for the button that re-launches the tour.
   *
   * @event do:set:helpactions
   * @param View actionView View that controls the display and UI events 
   *     for action buttons at the top of the help content in the drawer.
   */

  /**
   * Unset the view that defines action buttons that appear at the top of
   * the help content in the drawer.
   *
   * Currently, this is just used for the button that re-launches the tour.
   *
   * @event do:clear:helpactions
   */
   
   /**
    * Hide any detail panes associated with StoryTemplateViews.
    *
    * @event do:hide:template:detail
    */

  /**
   * Master view for the story builder
   *
   * Dispatches to sub-views.
   *
   * TODO: Document the options for this view
   *
   */
  Views.AppView = Backbone.View.extend({
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
      visibleSteps: VISIBLE_STEPS, 
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
      this.toolsView = new ToolsView(
        _.defaults({
          previewURLTemplate: this.options.previewURLTemplate
        }, commonOptions)
      );
      $toolsContainerEl.append(this.toolsView.el);

      this.helpView = new HelpView(
        _.clone(commonOptions)
      );
      this.drawerView = new DrawerView({
        dispatcher: this.dispatcher
      });
      this.drawerView.registerView(this.helpView);

      if (this.model) {
        commonOptions.model = this.model;
      }

      // Initialize the view for the workflow step indicator
      this.workflowStepView = new WorkflowStepView(
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
        selecttemplate: new SelectStoryTemplateView({
          dispatcher: this.dispatcher,
          collection: this.options.storyTemplates
        })
      };

      // Create views for additional workflow steps if they're enabled
      // in options. We don't iterate through the steps because the
      // views use different constructor, options. If this gets to
      // unwieldy, maybe use a factory function.
      if (this.options.visibleSteps.tag) {
        this.subviews.tag =  new TaxonomyView(
          _.defaults({
            places: this.options.places,
            topics: this.options.topics,
            organizations: this.options.organizations,
            projects: this.options.projects
          }, commonOptions)
        );
      }
      if (this.options.visibleSteps.review) {
        this.subviews.review = new ReviewView(
          _.clone(commonOptions)
        );
      }
      if (this.options.visibleSteps.publish) {
        this.subviews.publish =  new PublishView(
          _.defaults({
            defaultImageUrl: this.options.defaultImageUrl,
            showSharing: this.options.showSharing,
            licenseEndpoint: this.options.licenseEndpoint,
            viewURLTemplate: this.options.viewURLTemplate
          }, commonOptions)
        );
      }

      this.subviews.alert = new AlertManagerView({
        el: this.$(this.options.alertsEl),
        dispatcher: this.dispatcher
      });

      // IMPORTANT: Create the builder view last because it triggers
      // events that the other views need to listen to
      this.subviews.build = new BuilderView(buildViewOptions);
      this.lastSavedView = new LastSavedView({
        dispatcher: this.dispatcher,
        lastSaved: this.model ? this.model.get('last_edited'): null
      });
      this.$workflowContainerEl.append(this.lastSavedView.render().el);

      // Bind callbacks for custom events
      this.dispatcher.on("open:drawer", this.openDrawer, this);
      this.dispatcher.on("close:drawer", this.closeDrawer, this);
      this.dispatcher.on("select:template", this.setTemplate, this);
      this.dispatcher.on("select:workflowstep", this.updateStep, this); 
      this.dispatcher.on("error", this.error, this);
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
     * 
     * @param {String} step ID of the workflow step to set.  Must be one 
     *     of "build", "data", "tag", "review" or "publish"
     * @param {Function} [callback] Callback function that will be called
     *     after the active workflow step is set.
     */
    updateStep: function(step, callback) {
      var activeView;
      // Checking that step is different from the active step is
      // required for the initial saving of the story.  The active view
      // has already been changed by ``this.setTemplate`` so we don't
      // want to re-render.  In all other cases the changing of the 
      // active view is initiated by the router triggering the ``select:
      // workflowstep`` signal
      if (this.activeStep != step) {
        activeView = this.getActiveView();
        if (activeView && activeView.onHide) {
          activeView.onHide();
        }
        this.activeStep = step;
        this.render();
      }
      if (callback) {
        callback();
      }
    },

    /**
     * Get the sub-view for the currently active step
     */
    getActiveView: function() {
      return this.subviews[this.activeStep];
    },

    /**
     * Update the next/previous workflow step buttons
     */
    renderWorkflowNavView: function(activeView) {
      if (this._activeWorkflowNavView) {
        // Remove the previous active workflow nav view
        this._activeWorkflowNavView.$el.remove();
      }
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
      var activeView = this.getActiveView();
      var $container = this.$(this.options.subviewContainerEl);
      // Lookup for getting/setting the cookie to determine if the user
      // has already seen and closed the unsupported browser warning
      var cookieKey = 'storybase_hide_browser_support_warning';

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
      if (!this.checkBrowserSupport() && !$.cookie(cookieKey)) {
        // If the user has an unsupported browser and hasn't already seen
        // and closed the message, show an alert
        this.dispatcher.trigger('alert', 'error', this.options.browserSupportMessage, {
          // Don't automatically close the alert
          timeout: null,
          // When the alert is closed, set a cookie so the alert is not shown
          // again
          onClose: function() {
            $.cookie(cookieKey, true, {
              path: '/',
              expires: 365
            });
          },
          sticky: true
        });
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
      this.dispatcher.trigger('alert', 'error', msg);
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

  var AlertManagerView = Views.AlertManagerView = Backbone.View.extend({
    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      // Track messages that are currently visible 
      this._visible = {};

      this.dispatcher.on("alert", this.showAlert, this);
    },

    _hashAlert: function(level, msg) {
      return level + ':' + msg;
    },
    
    /**
     * Callback for when an AlertView is closed
     *
     * Should be bound an AlertView's 'close' event
     */
    removeAlert: function(alertView) {
      this.clearVisible(alertView.options.level, alertView.options.message);
    },

    isVisible: function(level, msg) {
      if (this._visible[this._hashAlert(level, msg)]) {
        return true;
      }

      return false;
    },

    setVisible: function(level, msg) {
      this._visible[this._hashAlert(level, msg)] = true;
    },

    clearVisible: function(level, msg) {
      var key = this._hashAlert(level, msg);
      if (this._visible[key]) {
        delete this._visible[key];
      }
    },

    /**
     * Show an alert message.
     *
     * @param {String} level Message level. Used to style the message.
     * @param {String} msg Message text.
     * @param {Integer|null} [options.timeout=15000] Milliseconds to show the message
     *   before it is hidden. If null, the message remains visible.
     * @param {Boolean} [options.sticky] Stick the alert to the top of the list
     *
     */
    showAlert: function(level, msg, options) {
      var view, $sticky;
      options = options || {};
      options.timeout = _.isUndefined(options.timeout) ? 15000 : options.timeout;
      options.level = level;
      options.message = msg;

      // Check for duplicate messages and only show the message
      // if it's different.
      if (!this.isVisible(level, msg)) {
        view = new AlertView(options);
        $sticky = this.$('.sticky').last();
        if (options.sticky) {
          view.$el.addClass('sticky');
        }
        if ($sticky.length) {
          $sticky.after(view.render().el);
        }
        else {
          this.$el.prepend(view.render().el);
        }
        this.setVisible(level, msg);
        view.once('close', this.removeAlert, this);
        if (options.timeout) {
          view.fadeOut();
        }
      }
    }
  });

  var AlertView = Views.AlertView = Backbone.View.extend({
    tagName: 'div',

    className: 'alert',

    options: {
      closeButton: true,
      closeButtonHtml: '<button type="button" class="close"><i class="icon-remove-sign"></i></button>',
      closeButtonSelector: 'button.close'
    },

    events: function() {
      var events = {};
      if (this.options.closeButton) {
        events['click ' + this.options.closeButtonSelector] = "close";
      }
      return events;
    },

    render: function() {
      var view = this;
      var html = this.options.message;

      if (this.options.closeButton) {
        html = html + this.options.closeButtonHtml;
      }
      this.$el.addClass('alert-' + this.options.level);
      this.$el.html(html);
      
      return this;
    },

    /**
     * Trigger a fadeOut animation on the element, then remove the view
     *
     * This must be called after the view has been added to the DOM 
     */
    fadeOut: function() {
      if (this.options.timeout) {
        this.$el.fadeOut(this.options.timeout, _.bind(this.close, this)); 
      }
      return this;
    },

    close: function() {
      if (this.options.onClose) {
        this.options.onClose(this);
      }
      this.remove();
      this.trigger('close', this);
    }
  });

  var DrawerButtonView = Views.DrawerButtonView = Backbone.View.extend({
    tagName: 'div',

    className: 'btn',

    events: {
      'click': 'handleClick'
    },

    initialize: function() {
      this.buttonId = this.options.buttonId;
      this.dispatcher = this.options.dispatcher;
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
    }
  });

  /**
   * View to toggle other views in a slide-out drawer.
   */
  var DrawerView = Views.DrawerView = HandlebarsTemplateView.extend({
    options: {
      templateSource: $('#drawer-template').html(),
      controlsEl: '#drawer-controls',
      contentsEl: '#drawer-contents'
    },

    initialize: function() {
      this.compileTemplates();
      this.dispatcher = this.options.dispatcher;
      this.dispatcher.on('register:drawerview', this.registerView, this);
      this.dispatcher.on('unregister:drawerview', this.unregisterView, this);
      this.dispatcher.on('do:toggle:drawer', this.toggle, this);

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

  var HelpDrawerMixin = {
    drawerButton: function() {
      if (_.isUndefined(this.drawerButtonView)) {
        this.drawerButtonView = new DrawerButtonView({
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

  var BuildHelpActionsView = Views.BuildHelpActionsView = HandlebarsTemplateView.extend({
    options: {
      templateSource: $('#build-help-actions-template').html()
    },

    events: {
      'click #repeat-tour-button': 'repeatTour'
    },

    initialize: function() {
      this.compileTemplates();
      this.dispatcher = this.options.dispatcher;
    },

    render: function() {
      this.$el.html(this.template());
      return this;
    },

    /**
     * Show the tour again.
     */
    repeatTour: function() {
      if (hasAnalytics()) {
        _gaq.push(['_trackEvent', 'Buttons', 'View the tour again']);
      }
      this.dispatcher.trigger('do:hide:help');
      this.dispatcher.trigger('do:show:tour', true);
    }
  });

  var HelpView = Views.HelpView = HandlebarsTemplateView.extend(
    _.extend({}, HelpDrawerMixin, {
      tagName: 'div',

      className: 'help',

      options: {
        templateSource: $('#help-template').html(),
        actionsEl: '#help-actions'
      },

      initialize: function() {
        this.compileTemplates();
        this.dispatcher = this.options.dispatcher;
        this.help = null;
       
        this.$el.hide();

        this.dispatcher.on('do:show:help', this.show, this);
        this.dispatcher.on('do:set:help', this.set, this);
        this.dispatcher.on('do:clear:help', this.clear, this);
        this.dispatcher.on('do:hide:help', this.hide, this);
        this.dispatcher.on('do:set:helpactions', this.setActions, this);
        this.dispatcher.on('do:clear:helpactions', this.clearActions, this);
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
        this.render();
        this.delegateEvents();
        this.$el.show();
        if (jQuery().tooltipster) {
          this.$('.tooltip').tooltipster();
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

      clear: function() {
        this.help = null;
      },

      /**
       * Set the view for the action buttons.
       *
       * @param {View} actionsView View to use for the action buttons.
       */
      setActions: function(actionsView) {
        this.actionsView = actionsView;
      },

      /**
       * Unset the view for the help action buttons.
       */
      clearActions: function() {
        this.actionsView = null;
      },
     
      /**
       * Render the action buttons.
       */
      renderActions: function() {
        if (this.actionsView) {
          // Set the element for the actions view before rendering
          // Does it make more sense to let the view have it's own
          // element and just prepend it to HelpView's element?
          this.actionsView.setElement(this.$(this.options.actionsEl));
          this.actionsView.render();
        }
        return this;
      },

      render: function() {
        var context = _.extend({
          'autoShow': this.autoShow
        }, this.help);
        this.$el.html(this.template(context));
        this.renderActions();
        return this;
      }
    })
  );

  /**
   * Base class for views that represent a list of items that trigger
   * some action when clicked.
   */
  var ClickableItemsView = Views.ClickableItemsView = HandlebarsTemplateView.extend({
    items: [],

    options: {
      templateSource: {
        'item': $('#clickable-item-template').html()
      }
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

    initialize: function() {
      this.compileTemplates();
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
      var template = this.getTemplate('item');
      this.$el.append(template({
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
  var WorkflowNavView = Views.WorkflowNavView = ClickableItemsView.extend({ 
    tagName: 'div',

    className: 'workflow-nav',

    options: {
      templateSource: {
        'item': $('#workflow-nav-item-template').html()
      }
    },

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
      ClickableItemsView.prototype.initialize.apply(this, arguments);
      this.dispatcher = this.options.dispatcher;
      this.items = _.isUndefined(this.options.items) ? this.items : this.options.items;
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
        path = Builder.APP_ROOT + path;
      }
      return path;
    },


    handleClick: function(evt) {
      evt.preventDefault();
      var $button = $(evt.target);
      var item = this.getItem($button.attr('id'));
      var valid = _.isFunction(item.validate) ? item.validate() : true;
      var href;
      var route;
      if (!$button.hasClass("disabled") && !$button.parent().hasClass("disabled") && valid) { 
        href = $button.attr("href");
        // Strip the base path of this app
        route = href.substr(Builder.APP_ROOT.length);
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
  var WorkflowStepView = Views.WorkflowStepView = WorkflowNavView.extend({
    tagName: 'ol',

    id: 'workflow-step',

    className: 'nav',

    options: {
      templateSource: {
        'item': $('#workflow-item-template').html()
      }
    },

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
      if (this.options.visibleSteps.tag) {
        items.push({
          id: 'tag',
          title: gettext("Label your story with topics and places so that people can easily discover it on Floodlight"),
          text: gettext('Tag'),
          visible: true,
          enabled: 'isStorySaved',
          selected: false,
          path: 'tag/'
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
  var ToolsView = Views.ToolsView = ClickableItemsView.extend({
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
      ClickableItemsView.prototype.initialize.apply(this, arguments);
      this.dispatcher = this.options.dispatcher;
      this.items = this._initItems();
      this.activeStep = null;
      this.hasAssetList = false;
      this.previewURLTemplate = this.templates.previewUrl = this.compileTemplate(this.options.previewURLTemplate);

      this.dispatcher.on('ready:story', this.handleStorySave, this);
      this.dispatcher.on('save:story', this.handleStorySave, this);
      this.dispatcher.on("select:workflowstep", this.updateStep, this);
    },

    previewStory: function(evt) {
      if (!$(evt.target).hasClass("disabled")) {
        var url = this.previewURLTemplate({story_id: this.storyId});
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
        item.path = this.previewURLTemplate({story_id: this.storyId});
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
      return !_.isUndefined(this.storyId);
    }
  });

  /**
   * Story template selector
   */
  var SelectStoryTemplateView = Views.SelectStoryTemplateView = HandlebarsTemplateView.extend({
    tagName: 'ul',
   
    className: 'story-templates view-container',

    options: {
      templateSource: $('#story-template-list-template').html()
    },

    initialize: function() {
      this.compileTemplates(); 
      this.dispatcher = this.options.dispatcher;
      _.bindAll(this, 'addTemplateEntry');
    },

    addTemplateEntry: function(template) {
        var view = new StoryTemplateView({
          dispatcher: this.dispatcher,
          model: template
        });
        this.$el.append(view.render().el);
    },

    render: function() {
      this.$el.html(this.template());
      this.collection.each(this.addTemplateEntry);
      this.$el.find('.template:even').addClass('even');
      if (jQuery().tooltipster) {
        this.$('.tooltip').tooltipster();
      }
      return this;
    }

  });

  /**
   * Story template listing
   */
  var StoryTemplateView = Views.StoryTemplateView = HandlebarsTemplateView.extend({
    tagName: 'li',

    attributes: function() {
      return {
        // Use this instead of the className property so we can set the class
        // dynamically when the view is instantiated based on the model's 
        // slug
        'class': 'template ' + this.model.get('slug') 
      };
    },

    options: {
      templateSource: $('#story-template-template').html()
    },

    events: {
      "click a.show-details": "toggleDetailPane",
      "click h3 a": "select"
    },

    initialize: function() {
      this.compileTemplates(); 
      this.dispatcher = this.options.dispatcher;
      this.dispatcher.on('do:hide:template:detail', this.removeDetailPane, this);
    },

    render: function() {
      this.$el.html(this.template(this.model.toJSON()));
      return this;
    },

    getDetailsEl: function() {
      var templateClassName = this.model.get('slug');
      return this.$el.siblings('li.template-details.' + templateClassName + ':visible');
    },

    toggleDetailPane: function(e) {
      if (this.getDetailsEl().length) {
        // hide our own
        this.removeDetailPane();
      }
      else {
        // hide all and show our own
        this.dispatcher.trigger('do:hide:template:detail');
        this.showDetailPane();
      }
      e.preventDefault();
      return false;
    },

    removeDetailPane: function() {
      var $existingDetails = this.getDetailsEl();
      if ($existingDetails.length) {
        $existingDetails.slideUp($.proxy(function() {
          $existingDetails.remove();
          this.$el.find('.show-details').toggleClass('icon-chevron-right icon-chevron-down');
        }, this));
      }
    },
    
    showDetailPane: function() {
      var $insertAfter = this.$el;
      var isEven = this.$el.hasClass('even');
      var templateClassName = this.model.get('slug');
      if (isEven && this.$el.next('li').length) {
        $insertAfter = this.$el.next('li');
      }
      this.$el.find('.details')
        .clone()
        .append('<div class="divot' + (isEven ? '' : ' odd') + '"></div>')
        .wrap('<li class="template-details ' + templateClassName + '" style="display:none;">')
        .parent('li') // wrap returns wrapped elements, not wrapping element
          .insertAfter($insertAfter)
          .slideDown($.proxy(function() {
            this.$el.find('.show-details').toggleClass('icon-chevron-right icon-chevron-down');
            this.scrollToDetailPane();
          }, this));
    },
    
    scrollToDetailPane: function() {
      var pane = this.$el.parent().find('.template-details.' + this.model.get('slug') + ':visible');
      if (pane.length) {
        var slop = 100;
        var paneTop = pane.position().top + slop;
        if (paneTop > $(window).scrollTop() + $(window).height()) {
          $(window).scrollTop(paneTop);
        }
      }
    },
    
    /**
     * Event handler for clicking a template's link
     */
    select: function(e) {
      this.dispatcher.trigger("select:template", this.model);
      e.preventDefault();
    }
  });

  /**
   * Class to encapsulate builder tour logic.
   */
  var BuilderTour = function(options) {
    _.extend(this.options, options);
    this.initialize.apply(this, arguments);
  };

  _.extend(BuilderTour.prototype, HandlebarsTemplateMixin, {
    options: {
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
      }
    },

    initialize: function() {
      this.compileTemplates();
      this.dispatcher = this.options.dispatcher;
    },

    /**
     * Move a guider's element to the left or right.
     */
    nudge: function($guiderEl, amount) {
      var guiderElemLeft = parseInt($guiderEl.css("left").replace('px', ''), 10);
      var myGuiderArrow = $guiderEl.find(".guider_arrow");
      var arrowElemLeft = parseInt(myGuiderArrow.css("left").replace('px', ''), 10);
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
     *
     * @param {Boolean} [force=false] Force showing the tour, ignoring
     *    other checks.
     *     
     */
    showTour: function(force) {
      if (force) {
        return true;
      }

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

    /**
     * Show the tour.
     *
     * @param {Boolean} [force=false] Force showing the tour, ignoring
     *    other checks.
     */
    show: function(force) {
      var that = this;

      var bindNudge = function(myGuider) {
        $(myGuider.elem).bind("guiders.show", function() {
          that.nudgeIntoWindow($(this));
        });
      }; 

      // Set a cookie so the builder tour is not shown again
      var setCookie = function() {
        $.cookie("storybase_show_builder_tour", false, {
          path: '/',
          // Don't show the tour for a very long time
          expires: 365
        });
      };

      // Default options when constructing the guiders
      var defaultOpts = {
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
        xButton: true,
        onShow: bindNudge,
        onClose: setCookie
      };
      
      if (this.showTour(force)) { 
        guiders.createGuider(_.defaults({
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
          description: this.getTemplate('workflow-step-guider')(),
          next: 'section-list-guider'
        }, defaultOpts));
        guiders.createGuider(_.defaults({
          id: 'section-list-guider',
          attachTo: '#section-list',
          position: 6,
          title: gettext("This is your table of contents."),
          description: gettext('This bar shows the sections in your story.'),
          prev: 'workflow-step-guider',
          next: 'section-thumbnail-guider'
        }, defaultOpts));
        guiders.createGuider(_.defaults({
          id: 'section-thumbnail-guider',
          attachTo: '.section-thumbnail:first',
          position: 6,
          title: gettext("Select the section you want to edit."),
          description: gettext("Click on a section to edit it. The section you are actively editing is highlighted."),
          prev: 'section-list-guider',
          next: 'section-manipulation-guider'
        }, defaultOpts));
        guiders.createGuider(_.defaults({
          id: 'section-manipulation-guider',
          attachTo: '.section-thumbnail',
          position: 6,
          title: gettext("You can also add, move or delete sections."),
          description: this.getTemplate('section-manipulation-guider')(),
          prev: 'section-thumbnail-guider',
          next: 'preview-guider'
        }, defaultOpts));
        guiders.createGuider(_.defaults({
          id: 'preview-guider',
          attachTo: '#tools .preview',
          position: 6,
          title: gettext("Preview your story at any time."),
          description: gettext("Clicking here lets you preview your story in a new window"),
          prev: 'section-manipulation-guider',
          next: 'exit-guider'
        }, defaultOpts));
        guiders.createGuider(_.defaults({
          id: 'exit-guider',
          attachTo: '#tools .exit',
          position: 6,
          title: gettext("You can leave your story at any time and come back later."),
          description: this.getTemplate('exit-guider')(),
          prev: 'preview-guider',
          next: 'help-guider'
        }, defaultOpts));
        guiders.createGuider(_.defaults({
          attachTo: '#drawer-controls [title="Help"]',
          position: 6,
          id: 'help-guider',
          title: gettext("Get tips on how to make a great story."),
          description: gettext("Clicking the \"Help\" button shows you tips for the section you're currently editing. You can also click on the \"?\" icon next to an asset to find more help."),
          onShow: function(myGuider) {
            bindNudge(myGuider);
            that.dispatcher.trigger('do:show:help');
          },
          next: 'repeat-tour-guider'
        }, defaultOpts));
        guiders.createGuider(_.defaults({
          attachTo: '#repeat-tour-button',
          position: 9,
          offset: { left: 10, top: 11 },
          id: 'repeat-tour-guider',
          title: gettext("View this tour again"),
          description: gettext("You can view this tour again by clicking this icon."),
          onHide: function() {
            that.dispatcher.trigger('do:hide:help');
          },
          next: 'tooltip-guider'
        }, defaultOpts));
        guiders.createGuider(_.defaults({
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
            setCookie();
            $('#workflow-step #build').triggerHandler('mouseout');
          }
        }, defaultOpts));
        guiders.show('workflow-step-guider');
        // HACK: Workaround for #415.  In IE, re-nudge the first guider element
        // after waiting a little bit. In some cases, the initial CSS change 
        // above doesn't render properly. The pause seems to fix this.  Note
        // that this uses the internal guiders API to get the element.
        if (MSIE) {
          setTimeout(function() {
            that.nudgeIntoWindow(guiders._guiderById('workflow-step-guider').elem);
          }, 250);
        }
      }
    }
  });

  var BuilderView = Views.BuilderView = Backbone.View.extend({
    tagName: 'div',

    className: 'builder',

    options: {
      titleEl: '.story-title',
      visibleSteps: VISIBLE_STEPS
    },

    initialize: function() {
      var that = this;
      var navViewOptions;
      var isNew = _.bind(function() {
        return !this.model.isNew();
      }, this);

      this.containerTemplates = this.options.containerTemplates;
      this.dispatcher = this.options.dispatcher;
      this.help = this.options.help;
      // Should the story relations be saved to the server?
      // Currently, we only want to do this once, when connected stories
      // are saved for the first time.
      this._saveRelatedStories = _.isUndefined(this.model) ? true : this.model.isNew() && this.options.relatedStories.length;
      this._tour = new BuilderTour({
        dispatcher: this.dispatcher,
        forceTour: this.options.forceTour,
        showTour: this.options.showTour
      });
      this.helpActionsView = new BuildHelpActionsView({
        dispatcher: this.dispatcher
      });

      if (_.isUndefined(this.model)) {
        // Create a new story model instance
        this.model = new Story({
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
      // The next step will either be tag (in the normal builder) or
      // publish (in the connected story builder). If this gets more
      // complicated, it might make more sense to have a global set
      // of items. 
      if (this.options.visibleSteps.tag) {
        navViewOptions.items.push({
          id: 'workflow-nav-tag-fwd',
          className: 'next',
          title: gettext("Label your story to help others discover it on Floodlight"),
          text: gettext("Next"),
          path: 'tag/',
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
      this.workflowNavView = new WorkflowNavView(navViewOptions);

      if (this.options.showSectionList) {
        this.sectionListView = new SectionListView({
          dispatcher: this.dispatcher,
          model: this.model
        });
      }
      this.unusedAssetView = new UnusedAssetView({
        dispatcher: this.dispatcher,
        assets: this.model.unusedAssets
      });

      this._editViews = [];

      this.model.on("sync", this.triggerSaved, this);
      this.model.sections.on("reset", this.triggerReady, this);
      this.model.unusedAssets.on("sync reset add", this.hasAssetList, this);

      this.dispatcher.on("select:template", this.setStoryTemplate, this);
      this.dispatcher.on("do:save:story", this.save, this);
      this.dispatcher.on("ready:story", this.createEditViews, this);
      this.dispatcher.on("save:story", this.setTitle, this);
      this.dispatcher.on("ready:story", this.setTitle, this);
      this.dispatcher.on("created:section", this.handleCreateSection, this);
      this.dispatcher.on('do:show:tour', this.showTour, this);

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
        language: this.options.language,
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
      view = new SectionEditView(options);
      this._editViews.push(view);
      return view;
    },

    createEditViews: function() {
      var storyEditView = null;
      var callEditView = null;
      if (this.options.showStoryInformation) {
        storyEditView = new StoryInfoEditView({
          dispatcher: this.dispatcher,
          help: this.help.where({slug: 'story-information'})[0],
          model: this.model
        });
        this._editViews.push(storyEditView);
      }
      this.model.sections.each(this.createSectionEditView); 
      if (this.options.showCallToAction) {
        callEditView = new CallToActionEditView({
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
      var that = this;
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
      this.showTour();

      this.dispatcher.trigger("register:drawerview", this.unusedAssetView);
      this.dispatcher.trigger('do:set:helpactions', this.helpActionsView);
    },

    onHide: function() {
      this.dispatcher.trigger('do:clear:help');
      this.dispatcher.trigger('do:clear:helpactions');
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

    triggerSaved: function() {
      this.dispatcher.trigger('save:story', this.model);
    },

    setStoryTemplate: function(template) {
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
      this.model.fromTemplate(this.templateStory, {
        language: this.options.language
      });
      this.dispatcher.trigger("ready:story", this.model);
    },

    saveRelatedStories: function() {
      if (this._saveRelatedStories) {
        // Only save the related stories if they've never been saved before
        if (this.model.relatedStories.length) {
          // Only bother making the request if there is actually data to 
          // save 
          this.model.saveRelatedStories();
        }
        this._saveRelatedStories = false;
      }
    },

    save: function() {
      var that = this;
      var isNew = this.model.isNew();
      this.model.save(null, {
        success: function(model, response) {
          that.dispatcher.trigger('save:story', model);
          model.saveSections();
          that.saveRelatedStories();
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
    },

    /**
     * Show the tour.
     *
     * @param {Boolean} [force=false] Force showing the tour. Otherwise,
     *     it is only shown if the user has not already seen it.
     */
    showTour: function(force) {
      this._tour.show(force);
    }
  });

  var LastSavedView = Views.LastSavedView = Backbone.View.extend({
    tagName: 'div',

    id: 'last-saved',

    options: {
      buttonId: 'save-button',
      buttonText: {
        'default': gettext("Save"),
        'saving': '<i class="icon-refresh icon-spin"></i> ' + gettext("Saving"),
        'saved': '<i class="icon-ok"></i> ' + gettext("Saved")
      },
      updateInterval: 5000,
      tooltipOptions: {
        position: 'right'
      }
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

    prettyDate: function(time) {
      return prettyDate(time, gettext);
    },

    initialize: function() {
      this.lastSaved = !!this.options.lastSaved ? this._makeStrict(this.options.lastSaved) : null;
      this.state = 'default';

      this.dispatcher = this.options.dispatcher;
      this.dispatcher.on("add:sectionasset", this.updateLastSaved, this);
      this.dispatcher.on('save:asset', this.updateLastSaved, this);
      this.dispatcher.on('save:section', this.updateLastSaved, this);
      this.dispatcher.on('save:story', this.updateLastSaved, this);
      this.dispatcher.on('ready:story', this.showButton, this);
      this.dispatcher.on('do:save:story', this.setSaving, this); 

      this.$buttonEl = $('<button type="button">' + this.options.buttonText[this.state] + '</button>')
        .attr('id', this.options.buttonId)
        .attr('title', gettext("Click to save your story"))
        .hide()
        .appendTo(this.$el);

      setInterval(_.bind(this.render, this), this.options.updateInterval);

      if (jQuery().tooltipster) {
        this.$buttonEl.tooltipster(this.options.tooltipOptions);
      }
    },

    setState: function(state) {
      this.state = state;
      if (this.state === 'default') {
        this.$buttonEl.prop('disabled', false);
      }
      else {
        this.$buttonEl.prop('disabled', true);
      }
      this.$buttonEl.html(this.options.buttonText[this.state]);
    },

    setSaving: function() {
      this.setState('saving');
    },

    updateLastSaved: function() {
      var view = this;
      this.lastSaved = new Date(); 
      this.render();
      view.setState('saved');
      setTimeout(function() {
        view.setState('default');
      }, 4000);
    },

    showButton: function() {
      this.$buttonEl.show();
      return this;
    },

    handleClick: function(evt) {
      this.dispatcher.trigger('do:save:story');
    },

    render: function() {
      var date = this.prettyDate(this.lastSaved);
      if (date) {
        lastSavedStr = gettext('Last saved') + ' ' + date;
        this.$buttonEl.attr('title', lastSavedStr);
      }
      return this;
    }
  });

  var UnusedAssetDrawerMixin = {
    drawerButton: function() {
      if (_.isUndefined(this.drawerButtonView)) {
        this.drawerButtonView = new DrawerButtonView({
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

    drawerCloseEvents: 'do:hide:assetlist'
  };

  /** 
   * A list of assets associated with the story but not used in any section.
   */
  var UnusedAssetView = Views.UnusedAssetView = HandlebarsTemplateView.extend(
    _.extend({}, UnusedAssetDrawerMixin, {
      tagName: 'div',

      id: 'unused-assets',

      options: {
        templateSource: $('#unused-assets-template').html()
      },

      initialize: function() {
        this.compileTemplates(); 
        this.dispatcher = this.options.dispatcher;
        this.assets = this.options.assets;

        // When the assets are synced with the server, re-render this view
        this.assets.on("add reset sync remove", this.render, this);
        // When an asset is removed from a section, add it to this view
        this.dispatcher.on("remove:sectionasset", this.addAsset, this);
        this.dispatcher.on("do:show:assetlist", this.show, this);
        this.dispatcher.on("do:hide:assetlist", this.hide, this);
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

          if (assetJSON.url && assetJSON.type !== 'image') {
            attrs.url = assetJSON.url;
          }
          return attrs;
        });
        var context = {
          assets: assetsJSON
        };
        this.$el.html(this.template(context));
        // Enable draggable functionality using jQuery UI
        this.$('.unused-asset').draggable({
          revert: 'invalid',
          // Clone the element while dragging and append the cloned
          // element to the body. This allows us to display the draggable
          // element as it's being dragged, even though the container
          // element has ``overflow:hidden``
          helper: 'clone',
          appendTo: 'body'
        });
        return this;
      },

      /**
       * Event callback for when assets are removed from a section
       */
      addAsset: function(asset) {
        this.assets.push(asset);
      },

      show: function() {
        return this.$el.show();
      },

      hide: function() {
        return this.$el.hide();
      }
    })
  );

  var RichTextEditorMixin = {
    toolbarTemplateSource: $('#editor-toolbar-template').html(),
    characterCountTemplateSource: $('#editor-toolbar-character-counter').html(),
    characterCountLimit: false,
    characterCountTimer: null,
    editor: null,

    getEditorToolbarHtml: function() {
      return this.toolbarTemplateSource; 
    },

    getEditorToolbarEl: function() {
      if (_.isUndefined(this._editorToolbarEl)) {
        this._editorToolbarEl = $(this.getEditorToolbarHtml())[0];
        if (this.characterCountLimit) {
          $(this._editorToolbarEl).prepend(this.characterCountTemplateSource);
        }
      }
      return this._editorToolbarEl; 
    },

    /**
     * @param characterCountLimit Optionally pass a number to specify a limit.
     */
    getEditor: function(el, callbacks, characterCountLimit) {
      var view = this;
      this.characterCountLimit = !isNaN(characterCountLimit) ? characterCountLimit : false;
      var defaultCallbacks = {
        'focus': function() {
          $(this.toolbar.container).show();
          if (view.characterCountLimit) {
            view.startPollingCharacterCount();
          }
        },

        'blur': function() {
          if (this._okToHideToolbar) {
            $(this.toolbar.container).hide();
          }
          if (view.characterCountLimit) {
            view.stopPollingCharacterCount();
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
          view.updateCharacterCount();
        }
        
        // @todo: what we really want is a change event that fires on every 
        // visible change in the editor. for some reason, the published 
        // change events do not behave that way. if future versions of the 
        // wysihtml5 editor address this, or if we change editors, something
        // like the following should be used rather than polling.
        //
        // 'change': function() {
        //   view.updateCharacterCount();
        // }
      };

      var toolbarEl = this.getEditorToolbarEl();
      $(el).before(toolbarEl);
      this.editor = new wysihtml5.Editor(
        el,    
        {
          toolbar: toolbarEl, 
          parserRules: wysihtml5ParserRules
        }
      );
      callbacks = _.isUndefined(callbacks) ? {} : callbacks;
      _.defaults(callbacks, defaultCallbacks);
      _.each(callbacks, $.proxy(function(value, key, list) {
        this.editor.on(key, value);
      }, this));
      return this.editor;
    },
    
    // @todo: switch from polling to listening for events when wysihtml5 editor
    // hits version 0.5. @see https://github.com/PitonFoundation/atlas/issues/530
    // and @see https://github.com/xing/wysihtml5/issues/174
    // or, ideally, use a published change event if its behavior is fine-grained
    // enough. see note above.
    startPollingCharacterCount: function() {
      this.characterCountTimer = setInterval($.proxy(this.updateCharacterCount, this), 500);
    },

    stopPollingCharacterCount: function() {
      clearInterval(this.characterCountTimer);
    },
    
    updateCharacterCount: function() {
      if (this.editor && this.characterCountLimit) {
        var $counter = $(this.getEditorToolbarEl()).find('.character-counter');
        if ($counter.length) {
          var text = this.editor.getValue();
          
          // remove tags
          text = text.replace(/<(.*?)>/g, '');
          
          // "render" to convert entities to characters (eg, &lt;)
          text = $('<div/>').html(text).text();
        
          $counter.find('.count').html(text.length);
          var $warning = $counter.find('.warning');
          if ($warning.length) {
            if (text.length > this.characterCountLimit) {
              $warning.show();
            }
            else {
              $warning.hide();
            }
          }
        }
      }
    }
  };

  /**
   * View mixin for updating a Story model's attribute and triggering
   * a save to the server.
   */
  var StoryAttributeSavingMixin = {
    saveAttr: function(key, value) {
      if (_.has(this.model.attributes, key)) {
        this.model.set(key, value);
        if (this.model.isNew()) {
          this.dispatcher.trigger("do:save:story");
        }
        else {
          this.model.save();
        }
      }
    }
  };

  var ThumbnailHighlightMixin = {
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
   * Mixin for views that have a navigation subview
   */
  var NavViewMixin = {
    getWorkflowNavView: function() {
      return this.workflowNavView;
    }
  };

  /**
   * A table of contents for navigating between sections in the builder.
   */
  var SectionListView = Views.SectionListView = HandlebarsTemplateView.extend({
    tagName: 'div',
    
    id: 'section-list',

    className: 'section-list',

    options: {
      templateSource: $('#section-list-template').html()
    },

    events: {
      'click .spacer': 'clickAddSection',
      'sortupdate': 'handleSort',
      'mousedown .scroll-right': 'scrollRight',
      'mousedown .scroll-left': 'scrollLeft',
      'mouseup': 'stopScroll'
    },

    initialize: function() {
      this.compileTemplates();
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

      this.dispatcher.on("do:remove:section", this.removeSection, this);
      this.dispatcher.on("ready:story", this.addSectionThumbnails, this);

      _.bindAll(this, 'addSectionThumbnail');

      this.$el.html(this.template());
    },

    addSectionThumbnail: function(section, index) {
      var sectionId = section.isNew() ? section.cid : section.id;
      var view = new SectionThumbnailView({
        dispatcher: this.dispatcher,
        model: section
      });
      index = _.isUndefined(index) ? this._sortedThumbnailViews.length - 1 : index + 1; 
      this._sortedThumbnailViews.splice(index, 0, view);
      this._thumbnailViews[sectionId] = view;
      if (section.isNew()) {
        section.once('sync', this.updateSectionThumbnailId, this);
      }
      return view;
    },

    /**
     * Event callback to update the key for the map of seciton IDs to
     * views
     */
    updateSectionThumbnailId: function(section) {
      var view;
      if (!_.isUndefined(this._thumbnailViews[section.cid])) {
        view = this._thumbnailViews[section.cid];
        this._thumbnailViews[section.id] = view;
        delete this._thumbnailViews[section.cid];
      }
    },

    addStoryInfoThumbnail: function() {
      var view = new PseudoSectionThumbnailView({
        dispatcher: this.dispatcher,
        title: gettext("Story Information"),
        tooltip: gettext("This section has basic information people will see when browsing stories on the site"),
        pseudoSectionId: 'story-info'
      });
      this._sortedThumbnailViews.push(view);
      this._thumbnailViews[view.pseudoSectionId] = view;
    },

    addCallToActionThumbnail: function() {
      var view = new PseudoSectionThumbnailView({
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
      var spacerWidth;
      this._thumbnailWidth = this._thumbnailWidth ||  $thumbnails.eq(0).outerWidth(true);
      this._spacerWidth = this._spacerWidth || this.$('.sections .spacer').first().outerWidth(true);
      // Set a default spacer width if it hasn't already been defined or 
      // can't be detected from the DOM. This is needed because when a story
      // is initially created, there aren't any spacers.  They appear once
      // the story is saved.
      spacerWidth = this._spacerWidth || 32;
      var newWidth = ($thumbnails.length * this._thumbnailWidth) + (($thumbnails.length + 2) * spacerWidth);
      this.$('.sections').width(newWidth); 
    },

    render: function() {
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
      var index = $(evt.currentTarget).find('.add-section').data('index');
      this.addNewSection(index);
    },

    addNewSection: function(index) {
      // TODO: Better method of selecting layout for new section.  This one
      // breaks if you remove all sections
      var section = new Section({
        title: '',
        title_placeholder: '',
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

    _getThumbnailEl: function(index) {
      return this._sortedThumbnailViews[index].$('.section-thumbnail');
    },

    _forCond: function(i, direction, numTmb) {
      if (direction === 'right') {
        return (i < numTmb);
      }
      else {
        return (i >= 0);
      }
    },

    _forFinal: function(i, direction) {
      if (direction === 'right') {
        return i+1;
      }
      else {
        return i-1;
      }
    },

    /**
     * Check if a section thumbnail is fully visible in the table of
     * contents.
     *
     * @param {Object} $el jQuery object for the section thumbnail element
     * @param {String} direction Which side of the table of contents
     *     should be checked for visibility? Either 'left' or 'right'
     * @param clipLeft {Integer} Offset of the right hand side of
     *     the clipping element
     * @param clipRight {Integer} Offset of the right hand side of
     *     the clipping element
     * @returns {Boolean} true if the element is FULLY visible
     */ 
    _tmbVisible: function($el, direction, clipLeft, clipRight) {
      if (direction === 'right') {
        return $el.offset().left + $el.outerWidth() <= clipRight; 
      }
      else {
        return $el.offset().left >= clipLeft;
      }
    },

    /**
     * Get the index of the last visible section thumbnail
     *
     * @param {String} direction Which side of the table of contents
     *     should be checked for visibility? Either 'left' or 'right'
     * @param clipLeft {Integer} Offset of the right hand side of
     *     the clipping element
     * @param clipRight {Integer} Offset of the right hand side of
     *     the clipping element
     * @returns {Integer} Index (relative to this._sortedThumbnailViews)
     *     of the last visible section thumbnail
     */
    _getLastVisibleThumbnailIdx: function(direction, clipLeft, clipRight) {
      var numTmb = this._sortedThumbnailViews.length;
      var $tmb;
      var lastVisible;
      var i = (direction === 'right') ? 0 : numTmb - 1;
      for (i; this._forCond(i, direction, numTmb); i = this._forFinal(i, direction)) {
        $tmb = this._getThumbnailEl(i); 
        if (this._tmbVisible($tmb, direction, clipLeft, clipRight)) {
          lastVisible = i;
        }
        else {
          return lastVisible;
        }
      }
    },

    startScroll: function(direction) {
      var that = this;
      var $clip = this.$('.sections-clip');
      var clipOffset = $clip.offset();
      var clipLeft = clipOffset.left;
      var clipRight = clipOffset.left + $clip.innerWidth();
      var numTmb = this._sortedThumbnailViews.length;
      var lastIdx = this._getLastVisibleThumbnailIdx(direction, clipLeft, clipRight);
      var $tmb;
      var tmbLeft, tmbRight;
      var scrollVal = null;
   
      if (direction === 'right' && lastIdx < numTmb - 1) {
        lastIdx++;
        $tmb = this._getThumbnailEl(lastIdx);
        tmbRight = $tmb.offset().left + $tmb.outerWidth();
        scrollVal = "+=" + (tmbRight - clipRight);
      }
      else if (direction === 'left' && lastIdx > 0) {
        lastIdx--;
        $tmb = this._getThumbnailEl(lastIdx);
        tmbLeft = $tmb.offset().left;
        scrollVal = "-=" + (clipOffset.left - tmbLeft);
      }

      if (scrollVal) {
        $clip.animate({scrollLeft: scrollVal}, 'fast', function() {
          if (that._doScroll) {
            that.startScroll(direction);
          }
        });
      }
    },

    scrollLeft: function(evt) {
      evt.preventDefault();
      this._doScroll = true;
      this.startScroll('left');
    },

    scrollRight: function(evt) {
      evt.preventDefault();
      this._doScroll = true;
      this.startScroll('right');
    },

    stopScroll: function(evt) {
      evt.preventDefault();
      this._doScroll = false;
    }
  });

  var SectionThumbnailView = Views.SectionThumbnailView = HandlebarsTemplateView.extend(
    _.extend({}, ThumbnailHighlightMixin, {
      tagName: 'li',

      className: 'section-thumbnail-container',

      options: {
        templateSource: $('#section-thumbnail-template').html()
      },

      events: {
        "click .section-thumbnail": "select",
        "click .remove": "clickRemove"
      },

      initialize: function() {
        this.compileTemplates();
        this.dispatcher = this.options.dispatcher;
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
        this.dispatcher.trigger("select:section", this.model);
      },

      clickRemove: function(evt) {
        evt.preventDefault();
        evt.stopPropagation();
        this.dispatcher.trigger("do:remove:section", this.model);
      }
  }));

  var PseudoSectionThumbnailView = Views.PseudoSectionThumbnailView = HandlebarsTemplateView.extend(
    _.extend({}, ThumbnailHighlightMixin, {
      tagName: 'li',

      className: 'section-thumbnail-container pseudo',

      options: {
        templateSource: $('#section-thumbnail-template').html()
      },

      events: {
        "click": "select"
      },

      initialize: function() {
        this.compileTemplates();
        this.dispatcher = this.options.dispatcher;
        this.pseudoSectionId = this.options.pseudoSectionId;
        this.title = this.options.title;
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

  var PseudoSectionEditView = Views.PseudoSectionEditView = HandlebarsTemplateView.extend(
    _.extend({}, RichTextEditorMixin, StoryAttributeSavingMixin, {
      tagName: 'div',

      initialize: function() {
        this.compileTemplates();
        this.dispatcher = this.options.dispatcher;
        this.help = this.options.help;

        this.dispatcher.on('select:section', this.show, this);
      },

      show: function(id) {
        id = _.isUndefined(id) ? this.pseudoSectionId : id;
        if (id == this.pseudoSectionId) {
          this.$el.show();
          // For now, don't automatically show help
          //this.dispatcher.trigger('do:show:help', this.help.toJSON()); 
          this.dispatcher.trigger('do:set:help', this.help.toJSON());
        }
        else {
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
  var StoryInfoEditView = Views.StoryInfoEditView = PseudoSectionEditView.extend({ 

    className: 'edit-story-info edit-section',

    pseudoSectionId: 'story-info',

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
      summaryEl: 'textarea[name="summary"]',
      templateSource: $('#story-info-edit-template').html()
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
        },
        250
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
  var InlineStoryInfoEditView = Views.InlineStoryInfoEditView = HandlebarsTemplateView.extend(
    _.extend({}, StoryAttributeSavingMixin, {
      className: 'edit-story-info-inline',

      options: {
        titleEl: '[name="title"]',
        bylineEl: '[name="byline"]',
        templateSource: $('#story-info-edit-inline-template').html()
      },

      events: function() {
        var events = {};
        events['change ' + this.options.titleEl] = 'change';
        events['change ' + this.options.bylineEl] = 'change';
        return events;
      },

      initialize: function() {
        this.compileTemplates();
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
  var CallToActionEditView = Views.CallToActionEditView = PseudoSectionEditView.extend({ 
    className: 'edit-call-to-action edit-section',

    // The section edit views can be identified by the ID of their
    // sections, but these pseudo-section edit views need an
    // explicit identifier
    pseudoSectionId: 'call-to-action',

    options: {
      callToActionEl: 'textarea[name="call_to_action"]',
      connectedEl: 'input[name="allow_connected"]',
      connectedPromptEl: 'textarea[name="connected_prompt"]',
      templateSource: $('#story-call-to-action-edit-template').html()
    },

    events: function() {
      var events = {};
      events['change ' + this.options.callToActionEl] = 'change';
      events['change ' + this.options.connectedEl] = 'changeConnectedEl';
      events['change ' + this.options.connectedPromptEl] = 'change';
      return events;
    },

    changeConnectedEl: function(evt) {
      this.change(evt);
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
  var SectionEditView = Views.SectionEditView = HandlebarsTemplateView.extend({
    tagName: 'div',

    className: 'edit-section',


    options: {
      containerEl: '.storybase-container-placeholder',
      titleEl: '.section-title',
      selectLayoutEl: 'select.layout',
      templateSource: $('#section-edit-template').html()
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
      this.compileTemplates();
      this.assets = this.model.assets;
      this._unsavedAssets = [];
      this._doConditionalRender = false;
      this._firstSave = this.model.isNew();
      // Object to keep track of asset edit views.  Keys are
      // the container ids.
      this._assetEditViews = {};
      // Container ID that should have it's model updated from
      // this.assets when rendering asset views after a sync
      this._refreshModelForContainer = null;
      // Have the section assets been fetched at least once?
      this._assetsFetched = false;
      
      // Edit the story information within the section edit view
      // This is mostly used in the connected story builder
      if (this.options.showStoryInfoInline) {
        this.storyInfoEditView = new InlineStoryInfoEditView({
          dispatcher: this.dispatcher,
          model: this.story,
          prompt: this.options.prompt
        });
      }

      _.bindAll(this, 'renderAssetViews');
      this.dispatcher.on('do:add:sectionasset', this.addAsset, this);
      this.dispatcher.on('do:remove:sectionasset',
                         this.handleDoRemoveSectionAsset, this);
      this.dispatcher.on('select:section', this.show, this);
      this.model.on("change:layout", this.changeLayout, this);
      this.model.on("sync", this.saveSectionAssets, this);
      this.model.on("sync", this.conditionalRender, this);
      this.model.on("sync", this.triggerSaved, this);
      this.model.on("destroy", this.handleDestroy, this);
      this.assets.once("sync", this.setAssetsFetched, this);
      this.assets.on("sync", this.renderAssetViews, this);
    },

    close: function() {
      this.remove();
      this.undelegateEvents();
      this.unbind();
      this.dispatcher.off('do:add:sectionasset', this.addAsset, this);
      this.dispatcher.off('do:remove:sectionasset',
                         this.handleDoRemoveSectionAsset, this);
      this.dispatcher.off('select:section', this.show, this);
      this.model.off("change:layout", this.changeLayout, this);
      this.model.off("sync", this.saveSectionAssets, this);
      this.model.off("sync", this.conditionalRender, this);
      this.model.off("sync", this.triggerSaved, this);
      this.model.off("destroy", this.handleDestroy, this);
      this.assets.off("sync", this.renderAssetViews, this);
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

    /**
     * Create a new SectionAssetEditView for a given
     * container.
     *
     * @param {String} container Container ID
     * @param {Object} el DOM element from the layout template
     *   that will be the view's element.
     */
    createAssetEditView: function(container, el) {
      var containerTemplate;
      var options = {
        el: el,
        container: container, 
        dispatcher: this.dispatcher,
        language: this.options.language,
        section: this.model, 
        story: this.story,
        assetTypes: this.options.assetTypes
      };
      if (this.assets.length) {
        // If there are assets, bind them to the view with the appropriate
        // container
        options.model = this.assets.where({container: container})[0];
      }
      if (this.templateSection && this.containerTemplates.length) {
        containerTemplate = this.containerTemplates.where({
          section: this.templateSection.id,
          container: container 
        })[0];
        if (containerTemplate) {
          options.suggestedType = containerTemplate.get('asset_type');
          options.canChangeAssetType = containerTemplate.get('can_change_asset_type');
          options.help = containerTemplate.get('help');
        }
      }
      this._assetEditViews[container] = new SectionAssetEditView(options);
      return this._assetEditViews[container]; 
    },

    /**
     * Get the asset editing view for a given container
     */
    getAssetEditView: function(container) {
      return this._assetEditViews[container];
    },

    /**
     * Indicate that the assets have been fetched. 
     *
     * This should be connected to the ``sync`` event
     * of ``this.assets``.
     */
    setAssetsFetched: function() {
      this._assetsFetched = true;
    },

    renderAssetViews: function() {
      var view = this;
      var containerAssets;
      this.$(this.options.containerEl).each(function(index, el) {
        var container = $(el).attr('id');
        var assetEditView = view.getAssetEditView(container);
        if (!assetEditView) {
          // If there isn't a view for this container, create it
          assetEditView = view.createAssetEditView(container, el);
        }
        else if (assetEditView.el != el) {
          // If the view's element isn't the one detected in the DOM,  update 
          // the view's element. This occurs when switching back to the build 
          // step view from another workflow step
          assetEditView.setElement(el);
        }

        if (view._refreshModelForContainer === container) {
          // Update the model for the edit view for a particular
          // container. This is neccesary when the assets have been
          // re-fetched after the user has tried to create an asset
          // when one has already been assigned to the section/container
          view._refreshModelForContainer = null;
          containerAssets = view.assets.where({container: container});
          if (containerAssets.length && assetEditView.model != containerAssets[0]) {
            assetEditView.setModel(containerAssets[0]); 
            assetEditView.setState('display');
          }
        }

        assetEditView.render();
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
      if (this.model.isNew() || this._assetsFetched) {
        // The model is new (so there are no assets) or
        // they've already been fetched.  Just (re)render
        // the views for each asset in the section
        this.renderAssetViews();
      }
      else {
        // Editing an existing story, but the assets have
        // not yet been retrieved.  Fetch them, which
        // will in turn trigger ``this.renderAssetViews``
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
        this.$el.show();
        // For now, don't show help automatically
        //this.dispatcher.trigger('do:show:help', help); 
        this.dispatcher.trigger('do:set:help', help);
      }
      else {
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

    /**
     * Event handler for the 'change:layout' event.
     */
    changeLayout: function(evt) {
      this.setConditionalRender();
      if (this.assets.length) {
        this.removeAssets();
      }
      else {
        this.removeAssetEditViews();
      }
    },

    /**
     * Disassociate all assets with this section. 
     */
    removeAssets: function() {
      this.assets.each(function(asset) {
        this.removeAsset(asset, {
          removeView: true
        });
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
     * Remove all asset editing views
     */
    removeAssetEditViews: function() {
      _.each(this._assetEditViews, function(view, container) {
        view.close();
        delete this._assetEditViews[container];
      }, this);
    },

    /**
     * Remove the asset editing view for a particular asset
     */
    removeEditViewForAsset: function(asset) {
      var container = asset.get('container');
      var view = this._assetEditViews[container];
      if (view && view.model == asset) {
        view.close();
        delete this._assetEditViews[container];
      }
    },

    /**
     * Callback for when an asset is removed from the section
     *
     * This should be be bound to the do:removesectionasset event.
     *
     * @param {Section} Section from which the asset is to be removed
     * @param {Asset} Asset to be removed from the section
     */
    handleDoRemoveSectionAsset: function(section, asset) {
      if (section == this.model) {
        this.removeAsset(asset);
      }
    },

    /**
     * Remove an asset from this section
     *
     * @param asset Asset to be removed
     * @param {Object} [options] Options for performing this operation.
     * @param options.removeView Should the view for editing the asset also
     *        be removed.
     */
    removeAsset: function(asset, options) {
      options = options || {};
      var view = this;
      var sectionAsset = this.getSectionAsset(asset);
      sectionAsset.id = asset.id;
      sectionAsset.destroy({
        success: function(model, response) {
          if (options.removeView) {
            view.removeEditViewForAsset(asset);
          }
          view.assets.remove(asset);
          view.dispatcher.trigger("remove:sectionasset", asset);
          view.dispatcher.trigger("alert", "info", "You removed an asset, but it's not gone forever. You can re-add it to a section from the asset list");
        },
        error: function(model, response) {
          view.dispatcher.trigger("error", "Error removing asset from section");
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

    /**
     * Assign an asset to a particular container in this section.
     */
    saveSectionAsset: function(asset, container) {
      var view = this;
      this.getSectionAsset(asset, container).save(null, {
        error: function(sectionAsset, xhr, options) {
          // Could not assign an asset to the container.  In most cases
          // this is because the user already assigned an asset to the
          // container in another tab/window
          var msg = xhr.responseText;
          if (xhr.status === 400) {
            msg = gettext("Oops, couldn't add your asset here. This is probably because you already did so in another tab or window. Hold tight while we refresh this section's assets.");
          }
          view.dispatcher.trigger('error', msg);
          view.assets.remove(asset);
          // Re-fetch this section's assets from the server to get the
          // assets that were added in the other window/tab. The resulting
          // ``sync`` event will also force the UI to re-render.
          view._refreshModelForContainer = container;
          view.assets.fetch();
          // TODO: Should we add the asset to the story's asset list ?
        }
      });
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
        if (window.polyfills) {
          window.polyfills.placeholders();
        }
      }
    }
  });

  var DataSetFormView = Backbone.View.extend({
    /**
     * Get the Backbone Forms schema for the data set form
     */
    getFormSchema: function(model) {
      var schema;
      
      // Start with the schema defined in either the model instance
      // or class
      if (_.isUndefined(model)) {
        schema = DataSet.prototype.schema();
      }
      else {
        schema = model.schema();
      }

      // Update some labels
      schema.title.title = gettext("Data set name");
      schema.source.title = gettext("Data source");
      if (!_.isUndefined(schema.url)) {
        schema.url.title = gettext("Link to a data set");
      }
      if (!_.isUndefined(schema.file)) {
        schema.file.title = gettext("Or, upload a data file from your computer");
      }

      return schema;
    },

    /**
     * Handler for form submission
     */
    processForm: function(evt) {
      var errors = this.form.validate();
      if (!errors) {
        this.handleSave(this.form.getValue(), evt.target);
      }
      else {
        // Remove any previous error messages
        this.form.$('.bbf-model-errors').remove();
        if (!_.isUndefined(errors._others)) {
          this.form.$el.prepend('<ul class="bbf-model-errors">');
          _.each(errors._others, function(msg) {
            this.form.$('.bbf-model-errors').append('<li>' + msg + '</li>');
          }, this);
        }
      }
      evt.preventDefault();
      evt.stopPropagation();
    },

    handleSave: function(attrs, form) { }
  });

  /**
   * Form for adding a new data set and associating it with an asset
   *
   * Events:
   *
   * "create:dataset" (model, postSaveAction) - when the data set has been
   * succesfully saved to the server. ``model`` is the data set that was saved. ``postSaveAction`` is the suggested
   * action to take with the view. A value of ``add`` means to keep the view
   * visible. A value of ``close`` means to hide the view.
   */
  var AssetDataSetAddView = Views.AssetDataSetAddView = DataSetFormView.extend({
    events: {
      'submit form': 'processForm',
      'click [type="submit"]': 'clickSubmit',
      'click [type="reset"]': 'cancel'
    },

    initialize: function(options) {
      this.dispatcher = options.dispatcher;
      this.form = this.getForm();
      // Action to be taken after the form is submitted. Default is
      // 'close' which will hide this view. 'add' will show a blank
      // form allowing the user to add another
      this._postSaveAction = 'close'; 
      this.handleSave = this.addDataSet;
    },

    getForm: function() {
      return new Backbone.Form({
        schema: this.getFormSchema()
      });
    },

    resetForm: function() {
      // Remove the old form from the DOM and remove event listeners
      this.form.remove();
      // Initialize a new form view
      this.form = this.getForm();
      // Re-render this view to add the new form to the DOM
      return this.render();
    },

    render: function() {
      this.$el.append(
        this.form.render().$el
            .append("<input type='reset' value='" + gettext("Cancel") + "' />")
            .append("<input type='submit' name='save' value='" + gettext("Save") + "' />")
            .append("<input type='submit' name='save-and-add' value='" + gettext("Save and Add Another") + "' />")
      );
      return this;
    },

    /**
     * Handler for clicking a submit button
     */
    clickSubmit: function(evt) {
      if ($(evt.target).attr('name') === 'save-and-add') {
        this._postSaveAction = 'add';
      }
      else {
        this._postSaveAction = 'close'; 
      }
    },

    /**
     * Handler for clicking the "Cancel" button
     */
    cancel: function(evt) {
      this.trigger('click:cancel');
      // Without the call to stopPropagation, the click event will bubble
      // up to the parent view's event handlers.  This might be desireable
      // if we just want to jump to the display view instead of back to the
      // dataset list view
      evt.stopPropagation();
    },


    addDataSet: function(attrs, form) {
      var view = this;
      var file = null;
      var options = {
        success: function(model, response) {
          view.dispatcher.trigger('alert', 'success', "Data set added");
          view.resetForm();
          view.trigger('create:dataset', model, view._postSaveAction);
        },
        error: function(model, response) {
          view.dispatcher.trigger('error', 'Error saving the data set');
        }
      };

      if (attrs.file) {
        _.extend(options, {
          upload: true,
          form: $(form)
        });
      }

      this.collection.create(attrs, options);
    },

    unsetCollection: function() {
      this.collection = undefined;
    },

    setCollection: function(collection) {
      this.collection = collection;
    }
  });

  var DataSetEditView = Views.DataSetEditView = DataSetFormView.extend({
    className: 'edit-dataset-form-container',

    events: {
      'submit form': 'processForm',
      'click [type="reset"]': 'cancel'
    },

    initialize: function(options) {
      this.dispatcher = options.dispatcher;
      this.form = new Backbone.Form({
        model: this.model,
        schema: this.getFormSchema(this.model)
      });
      this.handleSave = this.saveDataSet;
    },

    render: function() {
      this.$el.append(
        this.form.render().$el
            .append("<input type='reset' value='" + gettext("Cancel") + "' />")
            .append("<input type='submit' name='save' value='" + gettext("Save Changes") + "' />")
      );
      return this;
    },

    /**
     * Handler for clicking the "Cancel" button
     */
    cancel: function(evt) {
      this.trigger('click:cancel');
      // Without the call to stopPropagation, the click event will bubble
      // up to the parent view's event handlers.  This might be desireable
      // if we just want to jump to the display view instead of back to the
      // dataset list view
      evt.stopPropagation();
    },

    saveDataSet: function(attrs, form) {
      var view = this;
      var file = null;
      var options = {
        success: function(model, response) {
          view.dispatcher.trigger('alert', 'success', "Data set saved");
          view.trigger('save:dataset', model);
        },
        error: function(model, response) {
          view.dispatcher.trigger('error', 'Error saving the data set');
        }
      };

      if (!_.isUndefined(attrs.file)) {
        _.extend(options, {
          upload: true,
          form: $(form)
        });
      }
      else if (_.has(attrs, 'file')) { 
        // The attributes have a ``file`` key, but it's undefined.
        // This means we're not updating the file field.  Just throw away
        // the undefined file attribute so we keep whatever value is in the
        // model
        delete attrs.file;
      }

      this.model.save(attrs, options);
    },

    unsetCollection: function() {
      this.collection = undefined;
    },

    setCollection: function(collection) {
      this.collection = collection;
    }
  });

  var AssetDataSetListView = Views.AssetDataSetListView = HandlebarsTemplateView.extend({
    options: {
      templateSource: {
        '__main': $('#asset-dataset-list-container-template').html(),
        'list': $('#asset-dataset-list-list-template').html()
      }
    },

    events: {
      'click button[type="reset"]': 'clickClose',
      'click .add-dataset': 'clickAdd',
      'click .remove-dataset': 'clickRemove',
      'click .edit-dataset': 'clickEdit'
    },

    bindModelEvents: function() {
      this.collection.on('add remove', this.renderList, this);
    },

    unbindModelEvents: function() {
      this.collection.off('add remove', this.renderList, this);
    },

    bindSubviewEvents: function() {
      this.addView.on('click:cancel', this.clickAddCancel, this);
      this.addView.on('create:dataset', this.handleAdd, this);
    },

    unbindSubviewEvents: function() {
      this.addView.off('click:cancel', this.clickAddCancel, this);
      this.addView.off('create:dataset', this.handleAdd, this);
    },

    /**
     * Initialize and fetch the asset's datasets collection
     */
    _initCollection: function() {
      var view = this;
      if (!_.isObject(this.model.datasets)) {
        this.model.setDataSets(new DataSets());
        this.collection = this.model.datasets;
        this.collection.fetch({
          success: function() {
            view._collectionFetched = true;
          }
        });
      }
      else {
        this.collection = this.model.datasets;
        // Since the dataset collection has been initialized, assume its
        // also been already fetched from the server.
        this._collectionFetched = true;
      }
    },

    initialize: function(options) {
      this.dispatcher = options.dispatcher;
      // Flag to indicate whether or not the colleciton has
      // been fetched yet. This is used to defer rendering
      // until after the collection has been fetched.
      this._collectionFetched = false;
      // Have the datasets been changed
      this.hasChanged = false;
      this._initCollection();
      this.addView = new AssetDataSetAddView({
        collection: this.collection,
        dispatcher: this.dispatcher
      });
      this.compileTemplates();
      this.bindModelEvents();
      this.bindSubviewEvents();
    },

    close: function() {
      this.unbindModelEvents();
      this.unbindSubviewEvents();
    },

    /**
     * Scroll the browser window so the top of an element is visible
     * just below the header.
     */
    scrollTo: function($el) {
      var $header = $('header:first');
      // Assume header is fixed, so the top is at 0
      var headerBottom = $header.outerHeight();
      var scrollTo = $el.offset().top - headerBottom;
      $('html, body').animate({
        scrollTop: scrollTo 
      }, 500);
    },

    hideAdd: function() {
      this.addView.$el.hide();
      return this;
    },

    showAdd: function() {
      this.addView.$el.show();
      this.scrollTo(this.addView.$el);
      return this;
    },

    hideList: function() {
      this.$('.dataset-list-container').hide();
      return this;
    },

    showList: function() {
      this.$('.dataset-list-container').show();
      return this;
    },

    renderList: function() {
      var template = this.getTemplate('list');
      var context = {
        collectionFetched: this._collectionFetched
      };

      if (!this._collectionFetched) {
        // If the collection has not yet been fetched,
        // defer rendering until the collection has
        // been fetched
        this.collection.once('reset', this.renderList, this);
      }
      else {
        context.datasets = this.collection.toJSON();
      }
      this.$('.dataset-list-container').html(template(context));
      this.delegateEvents();
      return this;
    },

    renderEdit: function() {
      if (this.editView) {
        this.$('.wrapper').append(this.editView.render().$el);
      }
      return this;
    },

    render: function() {
      this.$el.html(this.template());
      this.renderList();
      this.addView.setElement(this.$('.add-dataset-form-container')).
                  render().$el.hide();
      return this;
    },

    /**
     * Tell upstream views that the user has requested that
     * this view be closed
     */
    triggerClose: function() {
      this.trigger('close', this.hasChanged);
      this.hasChanged = false;
    },

    clickClose: function(evt) {
      this.triggerClose();
    },

    clickAdd: function(evt) {
      this.hideList().showAdd();
    },

    clickAddCancel: function() {
      this.hideAdd().showList();
    },

    /**
     * Event handler for ``create:dataset`` event
     */
    handleAdd: function(dataset, postSaveAction) {
      this.hasChanged = true;
      // Proxy the event upstream
      if (postSaveAction === 'close') {
        this.triggerClose();
        // Hide the add data set subview and show the
        // list of datasets
        this.hideAdd().showList();
      }
    },

    closeEdit: function(dataset) {
      this.editView.remove();
      this.editView = null;
      this.hideAdd().showList();
    },

    /**
     * Event handler for ``save:dataset`` event
     */
    handleEdit: function(dataset) {
      this.hasChanged = true;
      this.renderList();
      this.closeEdit();
    },
    
    clickRemove: function(evt) {
      var datasetId = $(evt.target).data('dataset-id');
      var model = this.collection.get(datasetId);
      this.collection.remove(model, {
        sync: true
      });
      this.hasChanged = true;
    },

    clickEdit: function(evt) {
      var datasetId = $(evt.target).data('dataset-id');
      var model = this.collection.get(datasetId);
      this.editView = new DataSetEditView({
        model: model,
        dispatcher: this.dispatcher
      });
      this.editView.once('click:cancel', this.closeEdit, this);
      this.editView.once('save:dataset', this.handleEdit, this);
      this.hideAdd().hideList().renderEdit();
      this.scrollTo(this.editView.$el);
    },

    unsetModel: function() {
      this.addView.unsetCollection();
      this.unbindModelEvents();
      this.model = undefined;
      this.collection = undefined;
    },

    setModel: function(model) {
      this.model = model;
      this._initCollection();
      this.bindModelEvents();
      this.addView.setCollection(this.collection);
    }
  });

  var SectionAssetEditView = Views.SectionAssetEditView = HandlebarsTemplateView.extend(
    _.extend({}, RichTextEditorMixin, {
      tagName: 'div',

      className: 'edit-section-asset',

      options: {
        wrapperEl: '.wrapper',
        templateSource: {
          'display': $('#section-asset-display-template').html(),
          'edit': $('#section-asset-edit-template').html(),
          'upload': $('#asset-uploadprogress-template').html(),
          'select': $('#section-asset-select-type-template').html(),
          'sync': $('#section-asset-sync-template').html(),
          'image-help': $('#image-help-template').html(),
          'text-help': $('#text-help-template').html(), 
          'video-help': $('#video-help-template').html()
        }
      },

      events: {
        "hover .wrapper": "toggleTypeListVisible",
        "click .asset-type": "selectType", 
        "click .remove": "handleClickRemove",
        "click .edit": "edit",
        "click .edit-data": "handleClickEditData",
        "click .help": "showHelp",
        'click input[type="reset"]': "cancel",
        'submit form.bbf-form': 'processForm',
        'drop': 'handleDrop'
      },

      states: ['select', 'display', 'edit', 'editData', 'sync'],

      initialize: function() {
        this.compileTemplates();
        this.modelOptions = {
          language: this.options.language
        };
        var modelOptions = _.extend({}, this.modelOptions);
        this.container = this.options.container;
        this.dispatcher = this.options.dispatcher;
        this.assetTypes = this.options.assetTypes;
        this.section = this.options.section;
        this.story = this.options.story;
        if (_.isUndefined(this.model)) {
          // If no model is passed to the constructor, create
          // an empty Asset model
          if (this.options.suggestedType) {
            modelOptions.type = this.options.suggestedType;
          }
          this.model = new Asset(modelOptions);
        }
        else {
          // If it's an existing model, initialize views for
          // associated data
          this.initializeDataViews(); 
        }
        _.bindAll(this, 'handleUploadProgress', 'editCaption'); 
        this.bindModelEvents();
        this.initializeForm();
        this.setInitialState();
      },

      bindModelEvents: function() {
        this.model.on("change", this.initializeForm, this);
        this.model.on("remove", this.handleModelRemove, this);
        if (this.model.isNew()) {
          this.model.once("sync", this.initializeDataViews, this);
        }
      },

      unbindModelEvents: function() {
        this.model.off("change", this.initializeForm, this);
        this.model.off("remove", this.handleModelRemove, this);
        this.model.off("sync", this.initializeDataViews, this);
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
       * Get a list of asset types, their labels, and properties. 
       * Properties on returned hash:
       *  type {string}
       *  name {string}
       *  suggested {bool}
       *  available {bool}
       */
      getAssetTypes: function() {
        var type = this.options.suggestedType;
        var result = [];
        var canChangeAssetType = _.isUndefined(this.options.canChangeAssetType) || this.options.canChangeAssetType;
        _.each(this.assetTypes, function(type) {
          var isSuggested = type.type == this.options.suggestedType;
          // note we don't modify this.assetTypes
          result.push(_.extend({}, type, { 
            suggested: isSuggested,
            available: canChangeAssetType || isSuggested
          }));
        }, this);
        return result;
      },

      /**
       * Event handler for adding a new data set to the asset
       */
      handleDataSetListClose: function(refresh) {
        var view;
        if (refresh) {
          // The user wants to close the add data set form
          view = this;
          this.setState('sync').render();
          // Refresh the asset model to get the updated rendered data set
          // list (in the model's ``content`` attribute).
          // Then switch to the display state and re-render
          this.model.fetch({
            success: function() {
              view.setState('display').render();
            },
            error: function() {
              // TODO: Handle this error in a more meaningful way, perhaps by
              // showing an alert. For now, just render the old information 
              view.setState('display').render();
            }
          });
        }
        else {
          this.setState('display').render();
        }
      },

      /**
       * Initialize subviews for related data sets
       *
       * The first time this method is called, it creates a new instance 
       * of the subviews. On subsequent calls, it binds the subviews to
       * this view's model. The latter behavior is useful for when the
       * model is updated, either because a new asset has been created
       * or an asset has been dragged and dropped from the unused asset
       * list.
       */
      initializeDataViews: function() {
        if (this.model.acceptsData()) {
          if (_.isUndefined(this.datasetListView)) {
            // There's no data set list view - create one
            this.datasetListView = new AssetDataSetListView({
              model: this.model,
              dispatcher: this.dispatcher
            });
            // If the cancel button is clicked inside the dataset
            // list view, or if a data set has been added and (without
            // choosing to add another) hide the data set list view and show the display
            // view
            this.datasetListView.on('close', this.handleDataSetListClose, this);
          }
          else {
            // There's already a data set list view - reuse it
            this.datasetListView.setModel(this.model);
          }
        }
      },

      render: function() {
        var context = {};
        var editableCallback = function(value, settings) {
          that.saveAttr($(this).data("input-name"), value);
          return value;
        };
        var state = this.getState();
        var template = this.getTemplate(state);
        var $wrapperEl;
        if (state === 'select') {
          context.assetTypes = this.getAssetTypes();
          context.help = this.options.help;
        }
        else if (state === 'display') {
          context.model = this.model.toJSON();
          // Set context variable to toggle display of icon to edit data
          context.acceptsData = this.model.acceptsData();
        }
        if (template) {
          this.$el.html(template(context));
        }
        else {
          this.$el.empty();
        }
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
        if (state === 'editData') {
          this.$el.append(this.datasetListView.render().el);
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
        if (!$(e.target).hasClass('unavailable')) {
          this.setType($(e.target).data('asset-type'));
        }
      },

      toggleTypeListVisible: function(e) {
        this.$el.find('.asset-types').toggleClass('collapsed');
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

      /**
       * Save the asset model to the server.
       *
       * This method mostly handles initializing the callbacks and options for 
       * Asset.save()
       *
       * @param {Object} attributes Model attributes to be passed to
       *     Asset.save()
       */
      saveModel: function(attributes) {
        var view = this;
        // Save the model's original new state to decide
        // whether to send a signal later
        var isNew = this.model.isNew();
        var storyLicense = this.story.get('license');
        var options;

        // If this is the initial save and the story has a license
        // defined and the asset has no explicit license defined, set the
        // asset license to that of the story.
        if (isNew && _.isUndefined(attributes.license) && storyLicense) {
          attributes.license = storyLicense;
        }

        // Initialize callbacks for saving the model
        options = {
          success: function(model) {
            view.setState('display').render();

            if (isNew) {
              // Model was new before saving, trigger an event telling listeners
              // that a new asset has been added to the section
              view.dispatcher.trigger("do:add:sectionasset", view.section,
                view.model, view.container
              );
            }
            else {
              view.dispatcher.trigger("save:asset", view.model);
            }
          },
          error: function(model, xhr) {
            // If we've switched to the upload progress view, switch back to the
            // form
            if (view.getState() === 'upload') {
              view.setState('edit').render();
            }
            view.dispatcher.trigger('error', xhr.responseText || 'error saving the asset');
          }
        };

        if (attributes.image && !_.isUndefined(this.form.fields.image) && !attributes.url) {
          // A new file is being uploaded, provide some
          // additional options to Story.save()
          _.extend(options, {
            upload: true,
            // The form element in case we need to
            // POST via an iframe
            form: this.form.$el,
            progressHandler: this.handleUploadProgress
          });

          if (!_.isString(attributes.image)) {
            // If the image field is not a string (meaning it's a File object),
            // remove the form so we can show the upload status. Otherwise, we need
            // to keep the form around to be able to access the file input
            // element when posting the form through a hidden IFRAME
            this.setState('upload').render();
          }
        }

        this.model.save(attributes, options); 
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
        var errors = this.form.validate();
        var data;
        var view = this;

        e.preventDefault();

        if (!errors) {
          data = this.form.getValue();
          this.saveModel(data);
        }
        else {
          // Remove any previous error messages
          this.form.$('.bbf-model-errors').remove();
          if (!_.isUndefined(errors._others)) {
            view.form.$el.prepend('<ul class="bbf-model-errors">');
            _.each(errors._others, function(msg) {
              view.form.$('.bbf-model-errors').append('<li>' + msg + '</li>');
            });
          }
        }
      },

      edit: function(evt) {
        evt.preventDefault();
        this.setState('edit').render();
      },

      /**
       * Event handler for clicking the remove icon
       */
      handleClickRemove: function(evt) {
        evt.preventDefault();
        this.dispatcher.trigger('do:remove:sectionasset', this.section, this.model);
      },

      /**
       * Event handler for clicking the edit data icon
       */
      handleClickEditData: function(evt) {
        evt.preventDefault();
        this.setState('editData').render();
      },

      /**
       * Update the model property of the view, taking event callbacks into
       * account
       */
      setModel: function(model) {
        // This view should no longer listen to events on this model
        this.unbindModelEvents();
        this.model = model; 
        // Listen to events on the new model
        this.bindModelEvents();
        this.initializeDataViews();
      },

      /**
       * Callback for when a model is removed from this.assets
       *
       * @param {Asset} model Asset model instance that was removed
       */
      handleModelRemove: function(model, collection) {
        // Check whether the model is being removed from the section's
        // asset list. It could also be removed from the unused asset
        // list
        if (collection === this.section.assets) {
          this.setModel(new Asset(this.modelOptions));
          this.setState('select').render();
          if (this.datasetListView) {
            this.datasetListView.unsetModel();
          }
        }
      },

      getAssetTypeHelp: function(type) {
        var help = this.getTemplate(type + '-help');
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
        var id = ui.draggable.data('asset-id');
        var view = this;
        if (id) {
          this.setModel(this.story.unusedAssets.get(id));
          // HACK: The call to this.story.unusedAssets.remove results in
          // removing the draggable element before the ``stop`` event is 
          // handled, causing an exception when the jQuery-UI tries to
          // update the cursor when the dragging stops. Delaying the call
          // seems to work around this.
          //
          // See http://stackoverflow.com/a/13151132/386210
          setTimeout(function() {
            view.story.unusedAssets.remove(view.model);
          }, 0);  
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

  var ReviewView = Views.ReviewView = HandlebarsTemplateView.extend(
    _.extend({}, NavViewMixin, {
      className: 'view-container',

      options: {
        templateSource: $('#review-template').html()
      },

      events: {
        'click .preview': 'previewStory'
      },

      initialize: function() {
        this.dispatcher = this.options.dispatcher;
        this.compileTemplates();
        this.previewed = false;
        // Need to bind validate to this before it's passed as a callback to
        // the WorkflowNavView instance
        _.bindAll(this, 'hasPreviewed');
        this.workflowNavView = new WorkflowNavView({
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

  var TaxonomyView = Views.TaxonomyView = HandlebarsTemplateView.extend(
    _.extend({}, NavViewMixin, {
      id: 'share-taxonomy',

      className: 'view-container',

      options: {
        templateSource: $('#share-taxonomy-template').html()
      },

      initialize: function() {
        this.dispatcher = this.options.dispatcher;
        this.compileTemplates();
        this.workflowNavView = new WorkflowNavView({
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
              id: 'workflow-nav-review-fwd',
              className: 'next',
              title: gettext("Review"),
              text: gettext("Next"),
              path: 'review/'
            }
          ]
        });
        this.addLocationView = new AddLocationView({
          model: this.model,
          dispatcher: this.dispatcher
        });
        this.tagView = new TagView({
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
            label: value[labelAttr]
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
          'places': _.pluck(this.model.get('places'), 'id')
        };
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

  var AddLocationView = Views.AddLocationView = HandlebarsTemplateView.extend({
    id: 'add-location',

    mapId: 'map',

    events: {
      'click #search-address': 'searchAddress',
      'click .delete': 'deleteLocation',
      'submit': 'addLocation'
    },

    options: {
      templateSource: {
        '__main':  $('#add-location-template').html(),
        'location': $('#add-location-location-item-template').html()
      }
    },

    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      this.compileTemplates();
      this.initialCenter = new L.LatLng(storybase.MAP_CENTER[0],
                                        storybase.MAP_CENTER[1]);
      this.initialZoom = storybase.MAP_ZOOM_LEVEL;
      this.collection = new Locations([], {story: this.model});
      this.pointZoom = storybase.MAP_POINT_ZOOM_LEVEL;
      this.latLng = null;
      this._collectionFetched = false;
      this.collection.on("reset", this.renderLocationList, this);
      this.collection.on("add", this.renderLocationList, this);
      this.collection.on("remove", this.renderLocationList, this);
    },

    render: function() {
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
      var template = this.getTemplate('location');
      this.$('#locations').empty(); 
      this.collection.each(function(loc) {
        this.$('#locations').append($(template(loc.toJSON())));
      }, this);
    },

    searchAddress: function(evt) {
      evt.preventDefault();
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

  var TagView = Views.TagView = HandlebarsTemplateView.extend({
    id: 'story-tags',

    options: {
      templateSource: $('#tags-template').html()
    },

    events: {
      'change #tags': 'tagsChanged'
    },

    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      this.compileTemplates();
      this.collection = new Tags(null, {
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
          url: storybase.API_ROOT + 'tags/',
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
        model.url = storybase.API_ROOT + 'tags/' + id + '/stories/' + this.model.id + '/';
        model.destroy();
      }
    }
  });


  var LicenseDisplayView = Views.LicenseDisplayView = Backbone.View.extend({
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
      var params = licenseStrToParams(license);
      // Set provision license text just so the user sees something
      this._licenseHtml = "<p>" + gettext("You selected the ") + license + " " + gettext("license. Retrieving license details ...") + "</p>";
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
      }).error(function() {
        that._licenseHtml = "<p>" + gettext("You selected the ") + license + " " + gettext("license.") + "</p>";
        that.render();
      });
    },

    render: function() {
      if (!this._licenseHtml) {
        this.getLicenseHtml();
      }
      else {
        this.$el.html(this._licenseHtml);
      }
    }
  });

  var LicenseView = Views.LicenseView = HandlebarsTemplateView.extend({
    id: 'share-license',

    events: {
      'change form': 'processForm'
    },

    options: {
      title: gettext("Select a license"),
      templateSource: {
        '__main': $('#share-license-template').html(),
        'commercial': $('#share-cc-commercial-template').html(),
        'derivatives': $('#share-cc-derivatives-template').html()
      }
    },

    schema: function() {
      return {
        'commercial': {
          type: 'Radio',
          title: '',
          options: this.getTemplate('commercial')(),
          validators: ['required']
        },
        'derivatives': {
          type: 'Radio',
          title: '',
          options: this.getTemplate('derivatives')(),
          validators: ['required']
        }
      };
    },
   
    setStory: function(story) {
      this.model = story;
    },

    initialize: function() {
      var license = this.model ? this.model.get('license') : null;
      var formVals = licenseStrToParams(license);
      this.compileTemplates();
      this.dispatcher = this.options.dispatcher;
      this.form = new Backbone.Form({
        schema: this.schema(),
        data: formVals
      });
      this.licenseDisplayView = new LicenseDisplayView({
        dispatcher: this.dispatcher,
        model: this.model,
        licenseEndpoint: this.options.licenseEndpoint
      });
      if (_.isUndefined(this.model)) {
        this.dispatcher.on("ready:story", this.setStory, this);
      }
    },

    completed: function() {
      return this.model && this.model.get('license');
    },

    setLicense: function(params) {
      this.model.set('license', licenseParamsToStr(params));
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
      this.$el.html(this.template({
        title: this.options.title,
        license: license
      }));
      this.$el.append(this.form.render().el);
      this.licenseDisplayView.setElement(this.$('#cc-license')).render();
      this.delegateEvents();

      return this;
    }
  });

  /**
   * Common functionality and initialization used throughout
   * subviews for the Publish workflow step.
   */
  var PublishViewBase = Views.PublishViewBase = HandlebarsTemplateView.extend({
    /**
     * Set the model for this view.
     * This should be used as a "ready:story" event handler.
     */
    setStory: function(story) {
      this.model = story;
      this.initListeners();
    },

    /**
     * Test for story published status.
     */
    storyPublished: function() {
      return this.model ? (this.model.get('status') === "published") : false;
    },

    initListeners: function() {
      // If the model isn't defined at initialization (usually when creating
      // a new story), wire up a listener to set it when the story is ready.
      if (_.isUndefined(this.model)) {
        this.dispatcher.once("ready:story", this.setStory, this);
      }
    },

    initialize: function() {
      this.compileTemplates();
      this.dispatcher = this.options.dispatcher;
      this.initListeners();
    }
  });

  var PublishView = Views.PublishView = PublishViewBase.extend(
    _.extend({}, NavViewMixin, {
      id: 'share-publish',

      className: 'view-container',

      options: {
        // Source of template for the main view layout
        templateSource: $('#share-publish-template').html(),
        // Selector for the element (defined in templateSource) that
        // shows the sharing widgets
        sharingEl: '.publish-sharing',
        // Selector for the element (defined in templateSource) that
        // contains the controls for a published story
        publishedButtonsEl: '#published-buttons',
        // Selector for the element (defined in templateSource) that 
        // contains the subviews
        subviewEl: '#publish-steps',
        // Selector for the element (defined in templateSource) that
        // contains the legal information for the story
        legalEl: '#share-legal'
      },

      initListeners: function() {
        if (_.isUndefined(this.model)) {
          this.dispatcher.once("ready:story", this.setStory, this);
        }
        else {
          this.listenTo(this.model, "change:status", this.handleChangeStatus);
        }
      },

      initialize: function() {
        var navViewOptions;
   
        PublishViewBase.prototype.initialize.apply(this);

        this._sharingWidgetInitialized = false;
        this.licenseView = new LicenseView({
          model: this.model,
          dispatcher: this.dispatcher,
          licenseEndpoint: this.options.licenseEndpoint,
          tagName: 'li'
        });
        this.featuredAssetView = new FeaturedAssetView({
          model: this.model,
          defaultImageUrl: this.options.defaultImageUrl,
          dispatcher: this.dispatcher,
          language: this.options.language,
          tagName: 'li'
        });
        this.legalView = new LegalView({
          dispatcher: this.dispatcher,
          model: this.model
        });
        this.buttonView = new PublishButtonView({
          dispatcher: this.dispatcher,
          model: this.model,
          tagName: 'li'
        });
        this.publishedButtonsView = new PublishedButtonsView({
          dispatcher: this.dispatcher,
          model: this.model,
          viewURLTemplate: this.options.viewURLTemplate
        });
        this.subviews = [this.licenseView, this.featuredAssetView, this.buttonView];

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
        this.workflowNavView = new WorkflowNavView(navViewOptions);
      },

      handleChangeStatus: function(story, statusVal, options) {
        if (statusVal === 'published') {
          if (!this._sharingWidgetInitialized) {
            // Initiialize the sharing widget once the model has synced
            // with the server
            this.initSharingWidget({delay:true});
          }
        }
        // Show/hide the share sidebar.
        this.renderSharing();
      },

      initSharingWidget: function(options) {
        options = options || {};
        this._sharingWidgetInitialized = true;
        if (options.delay) {
          // Wait until the status change has been saved to the
          // server before initializing the widget, otherwise the GET to
          // /stories/{{story_id}}/share-widget/ endpoint will fail
          this.model.once("sync", this.initSharingWidget, this);
          return;
        }
        this.$('.storybase-share-widget').storybaseShare();
      },

      renderSharing: function() {
        var $el = this.$(this.options.sharingEl);
        if (this.storyPublished()) {
          if (!this._sharingWidgetInitialized) {
            this.initSharingWidget();
          }
          $el.show();
        }
        else {
          $el.hide();
        }
      },

      /**
       * Add subview to the DOM.
       */
      addSubviewEl: function(el) {
        this.$(this.options.subviewEl).append(el);
      },

      render: function() {
        var context = {
          title: this.model.get('title'),
          showSharing: this.options.showSharing,
          storyId: this.model ? this.model.id : ''
        };
        this.$el.html(this.template(context));
        _.each(this.subviews, function(view) {
          this.addSubviewEl(view.render().el);
        }, this);
        this.legalView.setElement(this.$('#share-legal')).render();
        this.publishedButtonsView.setElement(this.$(this.options.publishedButtonsEl)).render();
        if (this.options.showSharing) {
          this.renderSharing();
        }
        this.workflowNavView.render();
        this.delegateEvents();
        return this;
      },

      onShow: function() {
        this.featuredAssetView.onShow();
      }
    })
  );

  var LegalView = Views.LegalView = PublishViewBase.extend({
    id: 'share-legal',

    options: {
      templateSource: $('#share-legal-template').html()
    },

    initListeners: function() {
      if (_.isUndefined(this.model)) {
        this.dispatcher.once("ready:story", this.setStory, this);
      }
      else {
        this.listenTo(this.model, "change:status", this.render);
      }
    },

    initialize: function() {
      PublishViewBase.prototype.initialize.apply(this);
      this._rendered = false;
      this.$el.hide();
    },

    render: function() {
      if (!this._rendered) {
        this.$el.html(this.template());
        this._rendered = true;
      }
      if (this.storyPublished()) {
        this.$el.hide();
      }
      else {
        this.$el.show();
      }
      return this;
    },

    completed: true
  });

  var FeaturedAssetDisplayView = Views.FeaturedAssetDisplayView = Backbone.View.extend({
    id: 'featured-asset-display',

    options: {
      title: gettext("Current image"),
      defaultImageAlt: gettext('Default story image')
    },

    initListeners: function() {
      if (this.model) {
        this.listenTo(this.model, "set:featuredasset", this.render);
      }
      else {
        this.dispatcher.once("ready:story", function(story) {
          this.model = story;
          this.initListeners();
        }, this);
      }
    },

    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      this.initListeners();
    },

    enabled: true,

    render: function() {
      var featuredAsset;

      if (this.model) {
        featuredAsset = this.model.getFeaturedAsset();  
        if (featuredAsset) {
          // If the model is defined and it has a featured asset,
          // display the featured asset.
          this.$el.html(featuredAsset.get('content'));
          return this;
        }
      }
     
      // The model isn't defined, or there's no featured asset, show the
      // default image
      this.$el.html('<img src="' + this.options.defaultImageUrl + 
                    '" alt="' + this.options.defaultImageAlt +
                    '" />');
      return this;
    }
  });

  var FeaturedAssetSelectView = Views.FeaturedAssetSelectView = HandlebarsTemplateView.extend({
    id: 'featured-asset-select',

    tagName: 'ul',

    events: {
      'click .asset': 'clickAsset'
    },

    options: {
      title: gettext("Select an image from the story"),
      templateSource: $('#featured-asset-select-template').html()
    },

    initListeners: function() {
      if (_.isUndefined(this.model)) {
        this.dispatcher.once("ready:story", this.setStory, this);
      }
      else {
        // Listen to the sync event rather than "add" because we want
        // to make sure added assets have their attributes populated
        // before trying to render.
        // TODO: Make sure this is called the correct number of times
        this.listenTo(this.model.assets, "sync", this.render);
        this.listenTo(this.model, "set:featuredasset", this.render);
      }
    },

    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      this.initListeners();
      this.compileTemplates();
    },

    setStory: function(story) {
      this.model = story;
      this.initListeners();
    },

    enabled: function() {
      return this.model && this.model.assets.length;
    },

    clickAsset: function(evt) {
      var that = this;
      var $targetEl = $(evt.currentTarget);
      var id = $targetEl.data('assetId');
      var selected = this.model.assets.get(id);
      var $oldSelected = this.$('.selected');
      // Change the highlighting for instant response
      $oldSelected.removeClass('selected');
      $targetEl.addClass('selected'); 
      this.model.setFeaturedAsset(selected, {
        error: function() {
          // Reset the highlighting
          $targetEl.removeClass('selected');
          $oldSelected.addClass('selected');
          that.dispatcher.trigger("error", "Error selecting featured image");
        }
      });
      evt.preventDefault();
    },

    getImageAssetsJSON: function() {
      var featuredAsset;

      if (this.model) {
        featuredAsset = this.model.getFeaturedAsset();
        return _.map(this.model.assets.where({type: 'image'}),
          function(model) {
            var j = model.toJSON();
            if (featuredAsset && model.id == featuredAsset.id) {
              j.selected = true;
            }
            return j;
          },
          this
        );
      }

      return [];
    },

    render: function() {
      var context = {
        assets: this.getImageAssetsJSON()
      };
      this.$el.html(this.template(context));
      return this;
    }
  });

  var FeaturedAssetAddView = Views.FeaturedAssetAddView = HandlebarsTemplateView.extend({
    id: 'featured-asset-add',

    options: {
      title: gettext("Add a new image"),
      templateSource: $('#asset-uploadprogress-template').html(),
      assetModelClass: Asset
    },

    events: {
      'submit form.bbf-form': 'processForm',
      'click [type="reset"]': "cancel"
    },

    initialize: function() {
      this.compileTemplates();
      this.dispatcher = this.options.dispatcher;
      this.initializeForm();
      this.initListeners();
      this._appendForm = true; // Append the form element on render
    },

    enabled: true,

    initListeners: function() {
      this.dispatcher.once('ready:story', this.setStory, this);
    },

    initializeForm: function() {
      if (this.form) {
        // If there was a previous version of the form, remove it from the 
        // DOM and detach event listeners 
        this.form.remove();
      }
      // Create a new form with a new bound model instance
      this.form = new Backbone.Form({
        model: new this.options.assetModelClass({
          language: this.options.language,
          type: 'image'
        })
      });
      this.updateFormLabels(); 
      this.form.render();
      // Set a flag to tell render() that the form element
      // needs to be appended to the view element
      this._appendForm = true;
      return this;
    },

    updateFormLabels: function() {
      if (this.form.schema.url) {
        this.form.schema.url.title = capfirst(gettext("enter the featured image URL"));
      }
      if (this.form.schema.image) {
        this.form.schema.image.title = capfirst(gettext("select the featured image from your own computer"));
      }
    },

    setStory: function(story) {
      this.model = story;
    },

    renderUploading: function() {
      this.$el.html(this.template());
      return this;
    },

    render: function(options) {
      options = options ? options : {};

      if (options.uploading) {
        return this.renderUploading();
      }

      if (this._appendForm) {
        this.form.$el.append('<input type="reset" value="' + gettext("Cancel") + '" />').append('<input type="submit" value="' + gettext("Save Changes") + '" />');
        this.$el.append(this.form.el);
        this._appendForm = false;
      }

      return this;
    },

    cancel: function() {
      this.trigger('cancel');
    },

    /**
     * Event handler for submitting form
     */
    processForm: function(e) {
      var errors = this.form.commit();

      e.preventDefault();

      if (!errors) {
        this.saveModel(this.form.model);
      }
      else {
        // Remove any previous error messages
        this.form.$('.bbf-model-errors').remove();
        if (!_.isUndefined(errors._others)) {
          this.form.$el.prepend('<ul class="bbf-model-errors">');
          _.each(errors._others, function(msg) {
            this.form.$('.bbf-model-errors').append('<li>' + msg + '</li>');
          }, this);
        }
      }
    },

    saveModel: function(model) {
      var view = this;
      var image = model.get('image');
      var options = {
        error: function(model) {
          view.dispatcher.trigger('error', gettext('Error saving the featured image'));
        },
        success: function(model, response) {
          view.model.setFeaturedAsset(model);
          view.model.assets.add(model);
          view.initializeForm().render();
        }
      };

      model.set('license', this.model.get('license'));

      if (image) {
        _.extend(options, {
          upload: true,
          form: this.form.$el,
          progressHandler: this.handleUploadProgress
        });

        if (!_.isString(image)) {
          this.render({uploading: true});
        }
      }

      model.save(null, options);
    }
  });


  var FeaturedAssetView = Views.FeaturedAssetView = HandlebarsTemplateView.extend({
    id: 'featured-asset',

    events: {
      'click .nav a': 'handleNavClick'
    },

    options: {
      title: gettext("Select a featured image"),
      templateSource: {
        '__main': $('#featured-asset-template').html(),
        'nav-item': '<li{{#if class}} class="{{class}}"{{/if}}><a href="#{{viewId}}">{{title}}</li>'
      },
      addViewClass: FeaturedAssetAddView,
      displayViewClass: FeaturedAssetDisplayView,
      selectViewClass: FeaturedAssetSelectView
    },

    /**
     * Set the initial featured asset from the story's image assets
     * if one has not already been set.
     *
     * This really only applies to already-created stories without
     * featured images.  Newly-created stories will have their featured
     * asset set by the handler.
     */
    setInitialFeaturedAsset: function() {
      var imgAsset;
      if (this.model && this.model.featuredAssets.length === 0 &&
          this.model.assets.length !== 0) {
        imgAsset = this.model.assets.find(function(asset) {
          return asset.get('type') === 'image';
        });
        if (imgAsset) {
          this.model.setFeaturedAsset(imgAsset);
        }
      }
    },

    initListeners: function() {
      if (this.model) {
        this.listenTo(this.model.assets, "add", this.render);
        this.listenTo(this.model, "set:featuredasset", this.handleFeaturedAsset);
        this.listenTo(this.addView, "cancel", this.switchToDisplay);
        if (this.model.featuredAssets.length === 0) {
          // If the model doesn't have a featured asset set, try to
          // set it when new assets are added to the story
          this.listenTo(this.model.assets, "add", this.handleAddAsset);
        }
      }
      else {
        this.dispatcher.once("ready:story", this.setStory, this);
      }
    },

    initialize: function() {
      this.dispatcher = this.options.dispatcher;
      this.compileTemplates();
      this.displayView = new this.options.displayViewClass({
        defaultImageUrl: this.options.defaultImageUrl,
        dispatcher: this.dispatcher,
        model: this.model
      });
      this.addView = new this.options.addViewClass({
        dispatcher: this.dispatcher,
        model: this.model,
        language: this.options.language
      });
      this.selectView = new this.options.selectViewClass({
        dispatcher: this.dispatcher,
        model: this.model
      });
      this._subviews = [this.displayView, this.addView, this.selectView];
      this._activeViewId = this.displayView.id;
      this._rendered = false;

      this.setInitialFeaturedAsset();
      this.initListeners();
    },

    // Always true because the default image will be used if the user
    // doesn't select an image.
    completed: true, 

    setStory: function(story) {
      this.model = story;
      this.model.setFeaturedAssets(
        new FeaturedAssets()
      );
      this.initListeners();
    },

    handleNavClick: function(evt) {
      var $targetEl = $(evt.target);
      if (!$targetEl.parent().hasClass('disabled') && !$targetEl.parent().hasClass('active')) {
        this.$('.nav li').removeClass('active');
        $targetEl.parent().addClass('active');
        this._activeViewId = $targetEl.attr('href').replace('#', '');
        this.render();
      }
      evt.preventDefault();
    },

    createNavContainer: function() {
      return $('<ul class="nav pills">').appendTo(this.$el);
    },

    getNavContainer: function() {
      return this.$('.nav');
    },

    getNavItem: function(view) {
      return this.getNavContainer().find('[href="#' + view.id + '"]').parent(); 
    },

    isActive: function(view) {
      return view.id == this._activeViewId;
    },

    appendNavItem: function(view) {
      var enabled = _.result(view, 'enabled');
      var template = this.getTemplate('nav-item');
      var $navItemEl = $(template({
          title: view.options.title,
          viewId: view.id
      })).appendTo(this.getNavContainer());
      if (!enabled) {
        $navItemEl.addClass('disabled');
      }
      if (this.isActive(view)) {
        $navItemEl.addClass('active');
      }
      return $navItemEl;
    },

    appendSubView: function(view) {
      this.appendNavItem(view);
      view.render();
      if (!this.isActive(view)) {
        view.$el.hide();
      }
      this.$el.append(view.$el);
    },

    updateSubView: function(view) {
      this.updateNavItem(view);
      if (this.isActive(view)) {
        view.$el.show();
      }
      else {
        view.$el.hide();
      }
    },

    updateNavItem: function(view) {
      var $navItemEl = this.getNavItem(view);
      if (this.isActive(view)) {
        $navItemEl.addClass('active');
      }
      else {
        $navItemEl.removeClass('active');
      }

      if (_.result(view, 'enabled')) {
        $navItemEl.removeClass('disabled');
      }
      else {
        $navItemEl.addClass('disabled');
      }
    },

    renderInitial: function() {
      this.$el.html(this.template({
        title: this.options.title
      }));
      _.each(this._subviews, this.appendSubView, this);
      this._rendered = true;

      return this;
    },

    render: function() {
      if (!this._rendered) {
        return this.renderInitial();
      }
      _.each(this._subviews, this.updateSubView, this); 
      return this;
    },

    onShow: function() {
      this.delegateEvents();
    },

    handleAddAsset: function(asset) {
      if (asset.get('type') === 'image') {
        // Wait until the file upload has completed and the asset model has synced
        // before setting it as the featured asset. This works around a race
        // condition where FeaturedAssetDisplayView would render before the
        // asset attributes were updated.
        asset.once('change:content', function(asset) {
          this.model.setFeaturedAsset(asset);    
        }, this);
      }
    },

    handleFeaturedAsset: function() {
      // A featured asset has been selected, stop looking for the
      // initial featured asset
      this.stopListening(this.model.assets, "add", this.handleAddAsset);
      this.switchToDisplay();
    },

    switchToDisplay: function() {
      this._activeViewId = this.displayView.id;
      return this.render();
    }
  });

  var PublishedButtonsView = Views.PublishedButtonsView = PublishViewBase.extend({
    id: 'published-buttons',

    events: {
      'click .unpublish': 'handleUnpublish',
      'click a.popup': 'handleView'
    },

    options: {
      templateSource: {
        '__main': $('#published-buttons-template').html(),
        'view-url':  '/stories/{{slug}}/viewer/'
      }
    },

    initListeners: function() {
      // If the model isn't defined at initialization (usually when creating
      // a new story), wire up a listener to set it when the story is ready.
      if (_.isUndefined(this.model)) {
        this.dispatcher.once("ready:story", this.setStory, this);
      }
      else {
        this.listenTo(this.model, "change:status", this.handleChangeStatus);
      }
    },

    initialize: function() {
      PublishViewBase.prototype.initialize.apply(this);
      this._rendered = false;
    },

    handleChangeStatus: function(story, statusVal, options) {
      if (statusVal == 'published') {
        this.render();
      }
    },

    handleUnpublish: function(evt) {
      evt.preventDefault();
      var that = this;
      var success = function(model, response) {
        that.dispatcher.trigger('alert', 'success', 'Story unpublished');
        that.render();
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

    render: function() {
      if (!this._rendered) {
        // We only need to render the contents once, after that
        // rendering just accounts to showing or hiding the element
        this.$el.html(this.template({
          url: this.model ? this.getTemplate('view-url')(this.model.toJSON()) : ''
        }));
        this._rendered = true;
      }
      if (this.storyPublished()) {
        this.$el.show();
      }
      else {
        this.$el.hide();
      }
      return this;
    }
  });

  var PublishButtonView = Views.PublishButtonView = PublishViewBase.extend({
    id: 'publish-button',

    events: {
      'click .publish': 'handlePublish'
    },

    options: {
      templateSource: $('#publish-button-template').html(),
      title: gettext("Publish your story")
    },

    initListeners: function() {
      if (_.isUndefined(this.model)) {
        this.dispatcher.once("ready:story", this.setStory, this);
      }
      else {
        this.listenTo(this.model, 'change:status', this.handleChangeStatus);
      }
    },

    handleChangeStatus: function(story, statusVal, options) {
      if (statusVal !== 'published') {
        this.render();
      }
    },

    handlePublish: function(evt) {
      var that = this;
      var triggerPublished = function(model, response) {
        that.dispatcher.trigger('alert', 'success', 'Story published');
      };
      var triggerError = function(model, response) {
        that.dispatcher.trigger('error', "Error publishing story");
      };
      this.model.save({'status': 'published'}, {
        success: triggerPublished, 
        error: triggerError 
      });
      this.render();
      evt.preventDefault();
    },

    enable: function() {
      this.$('.publish').prop('disabled', false);
    },

    disable: function() {
      this.$('.publish').prop('disabled', true);
    },

    render: function() {
      var published = this.storyPublished();
      this.$el.html(this.template({
        title: this.options.title,
        published: published
      }));
      return this;
    }
  });
})($, _, Backbone, storybase);
