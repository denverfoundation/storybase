;(function(window, $, _, Backbone, Modernizr, wysihtml5, guiders, storybase) {
  // We use Underscore's _.template() in a few places. Use Mustache-style
  // delimeters instead of ERB-style ones.
  _.templateSettings = {
    interpolate: /\{\{(.+?)\}\}/g
  };

  // If the tooltipster jQuery plugin isn't installed, mock it so we can
  // call $(...).tooltipster(...) without error
  if (!$.fn.tooltipster) {
    $.fn.tooltipster = function (options) {};
  }

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
  var getLabelText = storybase.forms.getLabelText;
  var capfirst = storybase.utils.capfirst;
  var geocode = storybase.utils.geocode;
  var hasAnalytics = storybase.utils.hasAnalytics;
  var licenseParamsToStr = storybase.utils.licenseParamsToStr;
  var licenseStrToParams = storybase.utils.licenseStrToParams;
  var openInNewWindow = storybase.openInNewWindow;
  var prettyDate = storybase.utils.prettyDate;
  var HandlebarsTemplateMixin = storybase.views.HandlebarsTemplateMixin;
  var HandlebarsTemplateView = storybase.views.HandlebarsTemplateView;
  var MutexGroupedInputForm = storybase.forms.MutexGroupedInputForm;
  var RichTextEditor = storybase.forms.RichTextEditor;


  /**
   * Default visible steps of the story builder workflow.  
   *
   * These are usually passed to AppView when it is initialized.  However,
   * these defaults are provided to better document the behavior of the
   * app and for testing independent of the server-side code.
   */
  var VISIBLE_STEPS = {
    build: true,
    info: true, 
    publish: true,
    tag: true
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
   * Event callback for updating the progress of an upload.
   */
  var handleUploadProgress = function(evt) {
    var percentage;
    if (evt.lengthComputable) {
      percentage = Math.round((evt.loaded * 100) / evt.total);
      this.$('.uploadprogress .meter > span').width(percentage + '%');
    }
  };

  /**
   * Utility for checking if a view's model is new.
   *
   * The value of the function's ``this`` value should be bound
   * to a view instance using ``_.bind()``.
   */
  var storySaved = function() {
    return _.isUndefined(this.model) ? false : !this.model.isNew();
  };

  /**
   * Master view for the story builder
   *
   * Dispatches to sub-views.
   *
   * @property {object} options - Options for this view. These options are in
   * addition to the ones supported by Backbone.View.
   *   In many cases, these are used to tell the Backbone views about page
   *   elements that have already been rendered server-side, avoid hard-coding
   *   URL paths and provide collections for defining relationships with other
   *   models.
   * @property {object} options.assetTypes - Array of supported asset types.
   *   The asset types are objects with ``name`` and ``type`` properties.
   * @property {ContainerTemplates} options.containerTemplates - Collection
   *   of models describing help, default asset types and other properties of
   *   a template story's section asset container. 
   * @property {Backbone.Events} options.dispatcher - Global event bus.
   *   This will be passed to subviews.
   * @property {Backbone.Collection} options.help - Collection of help items.
   *   These can be edited with the Django admin.  The ids of this collection
   *   correspond to the slugs of the DJango models.
   * @property {object} options.layouts - List of available section layouts.
   *   Layout objects have ``name``, ``layout_id`` and ``slug`` properties.
   * @property {object} options.organizations - List of available
   *   organizations that can be used to categorize the story. Organization
   *   items have ``organization_id`` and ``name`` properties.
   * @property {object} options.projects - List of available projects that can
   *   be used to categorize the story.
   *   Project items have ``project_id`` and ``name`` properties.
   * @property {string} options.alertsEl - Selector for DOM element where
   *   application alerts will be displayed.
   * @property {object} options.places - List of available places that can be
   *   used to categorize the story.
   *   Place items have ``id`` and ``name`` properties.
   * @property {StoryRelations} options.relatedStories - Collection of stories
   *   related to the current story or story that will be created. This is
   *   used to specify the seed story in connected story relationships.
   * @property {StoryTemplates} options.storyTemplates - Collection of
   *   available story templates. 
   * @property {object} options.startOverUrl - Path to launch a new instance
   *   of the builder.
   * @property {object} options.storyListUrl - Path to view that lists the
   *   current users stories.
   * @property {string} options.browserSupportMessage - Message displayed when
   *   the application is launched with an unsupported browser.
   * @property {string} options.language - Language code for translating
   *   application strings.
   * @property {object} options.partials - Map of Handlebars partials.
   * @property {object} options.visibleSteps - Visible workflow steps. Values
   *   should be truthy for a step, identified by the keys of this object, to
   *   be shown.
   * @property {string} options.prompt - Prompt for the story.
   * @property {Story} options.templateStory - Story that provides the
   *   structure for this story.
   * @property {boolean} options.showCallToAction - If truthy, allow the user
   *   to set a call to action for their stories.
   * @property {boolean} options.showSectionList - If truthy, show a list of
   *   sections that allows the user to navigate between story sections.
   *   and add or remove sections.
   * @property {boolean} options.showLayoutSelection - If truthy, show a widget that allows the user to change the layout of a story section.
   * @property {boolean} options.showSectionTitles - If truthy, allow the user
   *   to edit the section titles.
   * @property {boolean} options.showStoryInfoInline - If truthy, show the
   *   inputs for editing the story title and byline along with the content of
   *   the first section.
   * @property {boolean} options.showTour - If truthy, show a tour of the
   *   story builder.
   * @property {boolean} options.forceTour - If truthy, force showing a tour
   *   of the story builder, even if options.showTour is falsey.
   * @property {string} options.siteName 
   * @property {string} options.drawerEl - Selector for DOM element of the
   *   drawer.
   * @property {string} options.headerEl - Selector for DOM element of the
   *   header.
   * @property {string} options.subNavContainerEl - Selector for DOM element
   *   that will contain subnavigation controls for a particular workflow
   *   step, for example the story section navigation control.
   * @property {string} options.subviewContainerEl - Selector for DOM element
   *   of the main application views, in most cases the workflow steps.
   * @property {string} options.toolsContainerEl - Selector for DOM element of
   *   the tools menu ("Start Over", "Exit", etc.).
   * @property {string} options.workflowContainerEl - Selector for DOM element
   *   of the workflow step selection menu.
   * @property {string} options.titleEl - Selector for DOM element of the
   *   story's title.
   * @property {string} options.titleEl - Selector for DOM element of the
   *   story's author information.
   * @property {string} optons.logoEl - Selector for DOM element of the logo.
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
      toolsContainerEl: '#workflow-bar-contents',
      visibleSteps: VISIBLE_STEPS, 
      workflowContainerEl: '#workflow-bar-contents',
      titleEl: '#title-bar-contents',
      bylineEl: '#title-bar-contents .byline-container',
      logoEl: '#title-bar-contents .logo img'
    },

    events: {
      'click a.external': openInNewWindow
    },

    registerPartials: function() {
      _.each(this.options.partials, function(tmplSrc, name) {
        Handlebars.registerPartial(name, tmplSrc);
      });
    },

    initialize: function(options) {
      // Common options passed to sub-views
      var commonOptions = {
        dispatcher: this.options.dispatcher,
        language: this.options.language,
        startOverUrl: this.options.startOverUrl,
        storyListUrl: this.options.storyListUrl
      };
      var buildViewOptions;
      var workflowSteps = [];
      var $toolsContainerEl = this.$(this.options.toolsContainerEl);
      this.$workflowContainerEl = this.$(this.options.workflowContainerEl);

      // Register some partials used across views with Handlebars
      this.registerPartials();

      this.dispatcher = this.options.dispatcher;
      // The currently active step of the story building process
      // This will get set by an event callback 
      this.activeStep = null; 

      if (!options.showStoryInfoInline) {
        this.titleView = new TitleView({
          el: this.$(this.options.titleEl),
          model: this.model,
          dispatcher: this.dispatcher
        });
        this.titleView.render();
        if (_.isUndefined(this.model)) {
          // If this is a new story, show the title input initially
          this.titleView.once('set:model', function() {
            this.titleView.edit();
            this.titleView.$editor().tooltipster('show');
          }, this);
        }

        this.bylineView = new BylineView({
          el: this.$(this.options.bylineEl),
          model: this.model,
          dispatcher: this.dispatcher
        });
        this.bylineView.render();

        this.bylineView.on('edit', this.toggleByline, this); 
        this.titleView.on('edit', this.toggleTitle, this);
      }

      this.toolsToggleView = new ToolsToggleView({
        dispatcher: this.dispatcher
      });
      $toolsContainerEl.append(this.toolsToggleView.render().el);

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

      buildViewOptions = _.defaults({
        assetTypes: this.options.assetTypes,
        containerTemplates: this.options.containerTemplates,
        forceTour: this.options.forceTour,
        layouts: this.options.layouts,
        help: this.options.help,
        prompt: this.options.prompt,
        relatedStories: this.options.relatedStories,
        templateStory: this.options.templateStory,
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
      // views use different constructor options. If this gets to
      // unwieldy, maybe use a factory function.
     
      if (this.options.visibleSteps.info) {
        this.subviews.info = new StoryInfoView(
          _.defaults({
            defaultImageUrl: this.options.defaultImageUrl,
            help: this.options.help
          }, commonOptions)
        );
        workflowSteps.push(_.result(this.subviews.info, 'workflowStep'));
      }
      
      if (this.options.visibleSteps.publish) {
        this.subviews.publish =  new PublishView(
          _.defaults({
            showSharing: this.options.showSharing,
            licenseEndpoint: this.options.licenseEndpoint,
            viewURLTemplate: this.options.viewURLTemplate
          }, commonOptions)
        );
        workflowSteps.push(_.result(this.subviews.publish, 'workflowStep'));
      }

      if (this.options.visibleSteps.tag) {
        this.subviews.tag = new TaxonomyView(
          _.defaults({
            places: this.options.places,
            topics: this.options.topics,
            organizations: this.options.organizations,
            projects: this.options.projects
          }, commonOptions)
        );
        workflowSteps.push(_.result(this.subviews.tag, 'workflowStep'));
      }

      this.subviews.alert = new AlertManagerView({
        el: this.$(this.options.alertsEl),
        dispatcher: this.dispatcher
      });

      this.subviews.build = new BuilderView(buildViewOptions);
      workflowSteps.unshift(_.result(this.subviews.build, 'workflowStep'));

      // Initialize the views for navigating between workflow steps
      this.workflowStepView = new WorkflowStepView(
        _.extend(_.clone(commonOptions), {
          items: workflowSteps
        })
      );
      this.$workflowContainerEl.append(this.workflowStepView.el);

      this.workflowNextPrevView = new WorkflowNextPrevView(
        _.extend(_.clone(commonOptions), {
          items: workflowSteps
        })
      );
      this.$workflowContainerEl.append(this.workflowNextPrevView.el);

      this.lastSavedView = new LastSavedView({
        dispatcher: this.dispatcher,
        lastSaved: this.model ? this.model.get('last_edited'): null
      });
      this.$workflowContainerEl.append(this.lastSavedView.render().el);

      // IMPORTANT: Only call this after other subviews have been initialized
      // because it triggers events that other views need to listen to
      this.subviews.build.initStory();

      // Bind callbacks for custom events
      this.dispatcher.on("open:drawer", this.openDrawer, this);
      this.dispatcher.on("close:drawer", this.closeDrawer, this);
      this.dispatcher.on("select:template", this.setTemplate, this);
      this.dispatcher.on("select:workflowstep", this.updateStep, this);
      this.dispatcher.on("error", this.error, this);
      this.dispatcher.on("select:template", this.setStoryClass, this);
      this.dispatcher.on("select:section", this.handleSelectSection, this);

      if (_.isUndefined(this.model) || this.model.isNew()) {
        this.dispatcher.once("save:story", this.updatePath, this);
      }
    },

    close: function() {
      this.dispatcher.off("open:drawer", this.openDrawer, this);
      this.dispatcher.off("close:drawer", this.closeDrawer, this);
      this.dispatcher.off("select:template", this.setTemplate, this);
      this.dispatcher.off("select:workflowstep", this.updateStep, this); 
      this.dispatcher.off("error", this.error, this);
      this.dispatcher.off("select:template", this.setStoryClass, this);
      this.dispatcher.off("select:section", this.handleSelectSection, this);
      this.dispatcher.off("save:story", this.updatePath, this);

      _.each(this.subviews, function(view) {
        // Call the close() method, if it exists on the workflow step subviews.
        if (view.close) {
          view.close();
        }
      }, this);
    },

    /**
     * Trigger an event to update the browser path to reflect
     * the story ID.
     */
    updatePath: function(story) {
      var path = story.id + '/';
      path += this.activeStep === 'build' ? '' : this.activeStep + '/'; 
      this.dispatcher.trigger('navigate', path, {
        trigger: true 
      });
    },

    toggleViews: function(show, hide) {
      hide.toggle();
      show.once('display', function() {
        hide.toggle();
      });
    },

    toggleByline: function() {
      this.toggleViews(this.bylineView, this.titleView);
    },

    toggleTitle: function() {
      this.toggleViews(this.titleView, this.bylineView);
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
     *     of "build", "data", "tag", "info" or "publish"
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
        // Scroll to top of window
        window.scrollTo(0, 0);
      }
      if (callback) {
        callback();
      }
    },

    /**
     * Handler for the select:section event.
     *
     * Scroll to the top of the window.
     */
    handleSelectSection: function() {
      window.scrollTo(0, 0);
    },

    /**
     * Get the sub-view for the currently active step
     */
    getActiveView: function() {
      return this.subviews[this.activeStep];
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
      var orig, headerBottom, offsetTop;

      if ($header.length) {
        // Calculate the offset, factoring in scroll position
        offsetTop = $header.offset().top - $(window).scrollTop(); 
        orig = $el.css('margin-top');
        headerBottom = offsetTop + $header.outerHeight();
        $el.css('margin-top', headerBottom);
      }

      return this;
    },

    render: function() {
      var activeView = this.getActiveView();
      var $container = this.$(this.options.subviewContainerEl);
      // Lookup for getting/setting the cookie to determine if the user
      // has already seen and closed the unsupported browser warning
      var cookieKey = 'storybase_hide_browser_support_warning';

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

      if (this.workflowNextPrevView) {
        this.workflowNextPrevView.render();
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
    },

    setStoryClass: function() {
      // Give the top-level container element a class to indicate that the
      // app has initialized a Story model and bound it the various subviews.
      //
      // In particular, this causes the story title bar to be revealed.
      this.$el.addClass('has-story');
     
      // Setting the ``has-story`` class causes the title bar to be revealed
      // so we need to readjust the top padding on the subview container
      // and the drawer in order to accomodate the larger header.
      this.pushDown(this.$(this.options.subviewContainerEl));
      this.pushDown(this.drawerView.$el);
    }
  });


  /**
   * View that offers inline editing of a single model attribute
   */
  var InlineEditorView = Backbone.View.extend({
    options: {
      template: _.template('<input type="text" name="{{attr}}" value="{{value}}" placeholder="{{placeholder}}" title="{{editorTooltip}}" />')
    },

    events: function() {
      var events = {};
      events['click ' + this.options.displayEl] = 'handleClick';
      events['blur ' + this.options.editorEl] = 'handleBlur';
      events['keyup ' + this.options.editorEl] = 'handleKeyUp';
      return events;
    },

    initialize: function(options) {
      this.dispatcher = options.dispatcher;

      if (this.model) {
        this.bindModelEvents();
      }
      else {
        this.dispatcher.once("ready:story", this.setModel, this);
      }
    },

    bindModelEvents: function() {
      var changeEvent = 'change:' + this.options.attr;
      this.model.on(changeEvent, this.renderDisplay, this);
      //this.model.on(changeEvent, this.display, this);
      this.model.on(changeEvent, this.saveModel, this);
    },

    $display: function() {
      return this.$(this.options.displayEl);
    },

    $editor: function() {
      return this.$(this.options.editorEl);
    },

    render: function() {
      var val, inputHtml;

      if (this.model) {
        val = this.getVal() || ''; 
        inputHtml = this.options.template({ 
          attr: this.options.attr,
          value: val, 
          placeholder: this.options.placeholder,
          editorTooltip: this.options.editorTooltip
        });

        this.renderDisplay();

        // Add a tooltip to let users know the element is editable
        this.$display().attr('title', this.options.tooltip)
            .tooltipster({
              position: 'top-left'
            }); 

        // Add the hidden form element
        $(inputHtml).hide().appendTo(this.$el)
                    .tooltipster();

        this.extraRender();
      }

      return this;
    },

    /**
     * Update the display of the title with a new value
     */
    renderDisplay: function() {
      var displayVal = this.getVal() || this.options.displayDefault;
      var editVal = this.getVal() || '';
      this.$display().html(displayVal);
      this.$editor().val(editVal);
      return this;
    },

    /**
     * Hook for additional rendering in subclasses.
     */
    extraRender: function() {},

    setModel: function(model) {
      this.model = model;

      this.bindModelEvents();
      this.render();
      this.trigger('set:model');
    },

    getVal: function() {
      return this.model.get(this.options.attr);
    },

    setVal: function(val) {
      this.model.set(this.options.attr, val);
    },

    edit: function() {
      this.$display().hide();
      this.$editor().show();
      this.trigger('edit');
    },

    display: function() {
      this.$editor().hide();
      this.$display().show();
      this.trigger('display');
    },

    handleClick: function(evt) {
      this.edit();
      this.$editor().focus();
      this._oldVal = this.getVal();
    },

    handleBlur: function(evt) {
      this.setVal($(evt.target).val());
      this.display();
    },

    handleKeyUp: function(evt) {
      var code = evt.which;

      // Only act when the enter key is the one that's pressed
      if (code == 13) {
        this.setVal($(evt.target).val());
        this.display();
      }
      else if (code == 27) {
        // Esc
        this.$editor().val(this._oldVal);
        this.display();
      }
    },

    saveModel: function() {
      if (this.model.isNew()) {
        // TODO: See if we can just get rid of the do:save:story signal
        // with cleaner event binding

        // If the story is new, trigger a "do:save:story" event on the
        // event bus so other views can take care of additional first-time
        // saving steps like updating the browser location and saving
        // sections.
        this.dispatcher.trigger('do:save:story');
      }
      else {
        this.model.save();
      }
      return this;
    },

    /**
     * Hook for toggling the display of the views elements.
     *
     * Because this view may operate on pre-existing elements, with
     * additional subelements, calling this.$el.toggle() might hide 
     * elements outside of the view's concern.
     */
    toggle: function() {
      this.$display().toggle();
    }
  });

  /**
   * View for displaying and editing the story title.
   */
  var TitleView = Views.TitleView = InlineEditorView.extend({
    options: _.defaults({
      attr: 'title',
      displayDefault: gettext("Untitled Story"),
      placeholder: gettext("Edit your title here. Shorter is better."),
      displayEl: '.title',
      editorEl: 'input[name="title"]',
      tooltip: gettext("Click to edit title"),
      editorTooltip: gettext("Enter your title. Press Enter to save or Esc to cancel.")
    }, InlineEditorView.prototype.options),

    extraRender: function() {
      // Add a character counter
      this.charCountView = new CharacterCountView({ 
        dispatcher: this.dispatcher,
        target: this.$editor(),
        warningLimit: 100,
        className: 'character-count'
      });
      this.$el.append(this.charCountView.render().$el);

      return this;
    }
  });

  var BylineView = Views.BylineView = InlineEditorView.extend({
    options: _.defaults({
      attr: 'byline',
      displayDefault: gettext("Unknown Author"),
      placeholder: gettext("Your Name and/or Organization. Examples: Jon Denzler; Laura Frank, I-News"),
      displayEl: '.byline',
      editorEl: 'input[name="byline"]',
      tooltip: gettext("Click to edit byline"),
      editorTooltip: gettext("Enter your byline. Press Enter to save or Esc to cancel.")
    }, InlineEditorView.prototype.options),

    $prefix: function() {
      return this.$('.byline-prefix');
    },

    edit: function() {
      this.$prefix().hide();
      InlineEditorView.prototype.edit.apply(this);
    },

    display: function() {
      this.$prefix().show();
      InlineEditorView.prototype.display.apply(this);
    },

    toggle: function() {
      return this.$el.toggle();
    }
  });

  var AlertManagerView = Views.AlertManagerView = Backbone.View.extend({
    initialize: function(options) {
      this.dispatcher = options.dispatcher;
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
     * @param {Integer|null} [options.timeout=8000] Milliseconds to show the message
     *   before it is hidden. If null, the message remains visible.
     * @param {Boolean} [options.sticky] Stick the alert to the top of the list
     * @param {String} [options.alertId] Id that can be used by other views to
     *   manage alerts they emit.
     *
     */
    showAlert: function(level, msg, options) {
      var view, $sticky;
      options = options || {};
      options.timeout = _.isUndefined(options.timeout) ? 8000 : options.timeout;
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
        this.dispatcher.trigger('show:alert', level, msg, view);
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

    initialize: function(options) {
      if (options) {
        this.alertId = options.alertId;
      }
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
        this.helpHistory = [];
       
        this.$el.hide();

        this.dispatcher.on('do:show:help', this.show, this);
        this.dispatcher.on('do:set:help', this.set, this);
        this.dispatcher.on('do:pop:help', this.pop, this);
        this.dispatcher.on('do:clear:help', this.clear, this);
        this.dispatcher.on('do:hide:help', this.hide, this);
        this.dispatcher.on('do:set:helpactions', this.setActions, this);
        this.dispatcher.on('do:clear:helpactions', this.clearActions, this);
      },

      /**
       * Show the help text.
       *
       * @param {Object} help Updated help information.  The object should have
       *     a body property and optionally a title property.
       * @param {Object} [opts] Hash of options:
       *     remember - Save the previous help value before replacing it
       *
       * @returns {Object} This view.
       */
      show: function(help, opts) {
        if (!_.isUndefined(help)) {
          // A new help object was sent with the signal, update
          // our internal value
          this.set(help, opts);
        }
        this.render();
        this.delegateEvents();
        this.$el.show();
        this.$('.tooltip').tooltipster();
        return this;
      },

      hide: function() {
        this.$el.hide();
      },

      /**
       * Set the help text.
       *
       * @param {Object} help Updated help information.  The object should have
       *     a body property and optionally a title property.
       * @param {Object} [opts] Hash of options:
       *     remember - Save the previous help value before replacing it
       */
      set: function(help, opts) {
        if (!_.isUndefined(opts) && opts.remember && this.help) {
          // Save the current help value before replacing it 
          this.helpHistory.push(this.help);
        }

        this.help = help;
        this.render();
      },

      /**
       * Set the help text to the last saved value
       */
      pop: function() {
        var help = null;
        if (this.helpHistory.length) {
          help = this.helpHistory.pop();
        }
        this.set(help);
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

    initialize: function(options) {
      ClickableItemsView.prototype.initialize.apply(this, arguments);
      this.dispatcher = options.dispatcher;
      this.items = options.items || [];
      // Include story ID in paths?  This should only happen for stories
      // created in this session.
      this._includeStoryId = _.isUndefined(this.model) ? false : this.model.isNew();
      if (_.isUndefined(this.model)) {
        this.dispatcher.on("ready:story", this.setStory, this);
      }

      this.activeStep = null;
      this.dispatcher.on("select:workflowstep", this.updateStep, this);

      this.extraInit(options);
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

    /**
     * Extra initialization operations
     *
     * Define this functionality in view subclasses.
     */
    extraInit: function() {},

    setStory: function(story) {
      this.model = story;
      this._includeStoryId = !this.model.isNew();
      this.dispatcher.once("save:story", this.handleInitialSave, this);
      this.render();
    },

    handleInitialSave: function(story) {
      this._includeStoryId = true;
      this.render();
    },

    getItemHref: function(itemOptions) {
      path = itemOptions.path;
      if (itemOptions.route !== false) {
        if (this._includeStoryId) {
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
    }
  });

  /**
   * Shows current and available steps of the builder workflow
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

    extraRender: function() {
      this.$('.tooltip').tooltipster({
        position: 'bottom'
      });
    }
  });

  /**
   * Next/previous buttons for navigating between workflow steps
   */
  var WorkflowNextPrevView = Views.WorkflowNextPrevView = WorkflowNavView.extend({
    extraInit: function(options) {
      this._itemIndexes = {};
      _.each(this.items, function(item, idx) {
        this._itemIndexes[item.id] = idx;  
      }, this);
    },

    updateStep: function(step) {
      var activeIdx, prevIdx, nextIdx;

      this.activeStep = step;
      this._prevStep = null;
      this._nextStep = null;
      
      activeIdx = this._itemIndexes[this.activeStep];
      if (!_.isUndefined(activeIdx)) {
        prevIdx = activeIdx - 1;
        nextIdx = activeIdx + 1;

        if (prevIdx >= 0) {
          this._prevStep = this.items[prevIdx].id;
        }

        if (nextIdx < this.items.length) {
          this._nextStep = this.items[nextIdx].id;
        }
      }

      this.render();
    },

    getItemClass: function(itemOptions) {
      var cssClass = WorkflowNavView.prototype.getItemClass.apply(this, arguments);
      var extra = "";

      if (itemOptions.id === this._prevStep) {
        extra = "prev";
      }
      else if (itemOptions.id === this._nextStep) {
        extra = "next";
      }

      extra = cssClass.length ? " " + extra : extra;

      cssClass = cssClass + extra;

      return cssClass;
    },

    getVisibleItems: function() {
      var items = [];
      if (!this.activeStep) {
        return items;
      }

      if (this._prevStep) {
        items.push(this.items[this._itemIndexes[this._prevStep]]);
      }

      if (this._nextStep) {
        items.push(this.items[this._itemIndexes[this._nextStep]]);
      }

      return items;
    }
  });

  /**
   * Button that opens and closes the tools menu.
   */
  var ToolsToggleView = Views.ToolsToggleView = Backbone.View.extend({
    tagName: 'button',

    id: 'tools-toggle',

    attributes: {
      type: 'button'
    },

    events: {
      'click': 'triggerToggle'
    },

    initialize: function(options) {
      this.dispatcher = options.dispatcher;
    },

    render: function() {
      this.$el.html('<span class="bar"></span><span class="bar"></span><span class="bar"></span>');
      return this;
    },

    triggerToggle: function() {
      this.dispatcher.trigger('toggle:tools');
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

    className: 'nav toggling',

    _initItems: function() {
      return [
        {
          id: 'my-stories',
          title: gettext("View a list of your stories"),
          text: gettext("My Stories"),
          path: this.options.storyListUrl,
          visible: true
        },
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
      this.dispatcher.on('select:workflowstep', this.updateStep, this);
      this.dispatcher.on('toggle:tools', this.toggle, this);
    },

    previewStory: function(evt) {
      if (!$(evt.target).hasClass("disabled")) {
        var url = this.previewURLTemplate({story_id: this.storyId});
        window.open(url);
      }
      // Close the menu
      this.toggle();
      evt.preventDefault();
    },

    toggle: function() {
      this.$el.slideToggle();
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
      this.$('.tooltip').tooltipster({
        position: 'left'
      });
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
      this.$('.tooltip').tooltipster();
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
      if (_.isUndefined(guiders)) {
        return;
      }

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
          title: gettext("Building a story takes four simple steps."),
          description: this.getTemplate('workflow-step-guider')(),
          next: 'title-byline-guider'
        }, defaultOpts));
        guiders.createGuider(_.defaults({
          id: 'title-byline-guider',
          attachTo: '#title-bar',
          position: 6,
          // By default, the guider is positioned at the middle of the
          // title-bar element.  Position it more to the left.
          offset: {
            left: -200,
            top: -50 
          },
          title: gettext("Edit your title and author information here."),
          description: gettext("Clicking on the title or author information here lets you set your story's title or your name and affiliation. Press Enter to save your changes.  You can edit the title or byline at any point during the story building process."), 
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
          next: 'preview-guider',
          // Open the tools menu so the next guider can be properly
          // positioned
          onHide: function() {
            that.dispatcher.trigger('toggle:tools');
          }
        }, defaultOpts));
        guiders.createGuider(_.defaults({
          id: 'preview-guider',
          attachTo: '#tools .preview',
          position: 9,
          title: gettext("Preview your story at any time."),
          description: gettext("Clicking here lets you preview your story in a new window"),
          prev: 'section-manipulation-guider',
          next: 'exit-guider'
        }, defaultOpts));
        guiders.createGuider(_.defaults({
          id: 'exit-guider',
          attachTo: '#tools .exit',
          position: 9,
          title: gettext("You can leave your story at any time and come back later."),
          description: this.getTemplate('exit-guider')(),
          prev: 'preview-guider',
          next: 'help-guider',
          // Close the tools menu so the next guider can be properly
          // positioned
          onHide: function() {
            that.dispatcher.trigger('toggle:tools');
          }
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
      titleEl: '.story-title'
    },

    workflowStep: {
      id: 'build',
      title: gettext("Construct your story using text, photos, videos, data visualizations, and other materials"),
      nextTitle: gettext("Write Your Story"),
      prevTitle: gettext("Continue Writing Story"),
      text: gettext("Build"),
      visible: true,
      path: ''
    },

    initialize: function() {
      var that = this;

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
      this.model.unusedAssets.on("sync reset add", this.hasAssetList, this);

      this.dispatcher.on("select:template", this.setStoryTemplate, this);
      this.dispatcher.on("do:save:story", this.save, this);
      this.dispatcher.on("ready:story", this.createEditViews, this);
      this.dispatcher.on("save:story", this.setTitle, this);
      this.dispatcher.on("ready:story", this.setTitle, this);
      this.dispatcher.on("created:section", this.handleCreateSection, this);
      this.dispatcher.on('do:show:tour', this.showTour, this);
    },

    /**
     * Fetch the story's sections from the server or copy them from a template
     * story.
     *
     * IMPORTANT! This should only be called after other views have been
     * initialized because it causes signals to be triggered on the
     * event bus that may need to be listened to by other views.
     */
    initStory: function() {
      if (!this.model.isNew()) {
        if (this.templateStory) {
          // If we know about a template story, get suggestions for
          // some story and section fields from the template. But, we
          // have to wait for the sections to sync first
          this.model.sections.once("reset", function(sections) {
            this.model.suggestionsFromTemplate(this.templateStory); 
            this.dispatcher.trigger('ready:story', this.model);
          }, this);
        }
        this.model.sections.fetch();
        this.model.unusedAssets.fetch();
      }
      else if (this.templateStory) {
        // Model is new, but a template was provided when the builder was launched
        // We don't have to wait to request the template from the server.
        this.initializeStoryFromTemplate();
      }
    },

    close: function() {
      this.model.off("sync", this.triggerSaved, this);
      this.model.unusedAssets.off("sync reset add", this.hasAssetList, this);

      this.dispatcher.off("select:template", this.setStoryTemplate, this);
      this.dispatcher.off("do:save:story", this.save, this);
      this.dispatcher.off("ready:story", this.createEditViews, this);
      this.dispatcher.off("save:story", this.setTitle, this);
      this.dispatcher.off("ready:story", this.setTitle, this);
      this.dispatcher.off("created:section", this.handleCreateSection, this);
      this.dispatcher.off('do:show:tour', this.showTour, this);
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
      var callEditView = null;

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
        this.dispatcher.trigger('select:section', this._editViews[0].getSection());
      }
    },

    render: function() {
      if (this.sectionListView) {
        this.sectionListView.render();
      }

      this.renderEditViews();

      return this;
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
      var view = this;
      var isNew = this.model.isNew();
      this.model.save(null, {
        success: function(model, response) {
          view.dispatcher.trigger('save:story', model);
          model.saveSections();
          view.saveRelatedStories();
          if (isNew && view.navView) {
            // Re-render the navigation view to enable the button
            view.navView.render();
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

      this.$buttonEl.tooltipster(this.options.tooltipOptions);
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
      $(evt.target).tooltipster('hide');
    },

    render: function() {
      var date = this.prettyDate(this.lastSaved);
      var lastSavedStr;
      if (date) {
        lastSavedStr = gettext('Last saved') + ' ' + date;
        this.$buttonEl.tooltipster('update', lastSavedStr);
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
          else if (assetJSON.body && assetJSON.type === 'text') {
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

  /**
   * Create a character count view attached to either an input or wysihtml5 editor.
   * 
   * Required parameter:
   * 
   * @param {Object|HTMLElement} options.target The wysihtml5 editor, or an input element.
   * 
   */
  var CharacterCountView = Views.CharacterCountView = HandlebarsTemplateView.extend({
    tagName: 'div',
    className: 'character-count',

    editor: null,
    editorType: null,
    timer: null,

    options: {
      templateSource: $('#character-count-template').html(),
      warningLimit: 250,
      warningText: 'Shorter is better!',
      countHTML: false,
      showOnFocus: true,
      target: null
    },

    initialize: function(options) {
      this.dispatcher = options.dispatcher;

      this.compileTemplates();

      this.setEditor(options.target);

      this.dispatcher.on('select:section', 
        this.handleSectionChanged, this
      );

      return this;
    },

    /**
     * Set the editor and bind DOM event handlers
     *
     * editor argument can either be a DOM element or a wysihmtl5.Editor
     * instance.
     */
    setEditor: function(editor) {
      if (editor instanceof wysihtml5.Editor) {
        this.editor = editor; 
        this.editorType = 'wysihtml5';
      }
      else {
        // assume a DOM element or jQuery-wrapped element
        this.editor = $(editor);
        this.editorType = 'node';
      }

      this.bindEditorEvents();

      return this;
    },

    /**
     * Bind DOM event handlers to the editor instance/element.
     */
    bindEditorEvents: function() {
      this.editor.on('focus', _.bind(this.handleEditorFocus, this));
      this.editor.on('blur', _.bind(this.handleEditorBlur, this));
      this.editor.on('change', _.bind(this.handleEditorChange, this));
      this.editor.on('load', _.bind(this.handleEditorLoad, this));
    },

    handleEditorFocus: function() {
      this.startPolling();
      if (this.options.showOnFocus) {
        this.$el.slideDown();
      }
    },
    
    handleEditorBlur: function() {
      this.stopPolling();
      if (this.options.showOnFocus) {
        this.$el.slideUp();
      }
    },
    
    handleEditorChange: function() {
      this.updateCharacterCount();
    },
    
    handleEditorLoad: function() {
      this.updateCharacterCount();
    },

    handleSectionChanged: function() {
      // Focus management seems a little sketchy around section changes.
      // We apparently can't rely on our editors to fire a blur event.
      this.stopPolling();
    },

    getEditorValue: function() {
      if (this.editorType == 'wysihtml5') {
        return this.editor.getValue();
      }
      return this.editor.val();
    },
    
    updateCharacterCount: function() {
      var text = this.getEditorValue();

      if (!this.options.countHTML) {
        // remove tags
        text = text.replace(/<(.*?)>/g, '');
        // "render" to convert entities to characters (eg, &lt;)
        text = $('<div/>').html(text).text();
      }

      this.$el.find('.count').html(text.length);
      if (text.length > this.options.warningLimit) {
        this.$el
          .addClass('over-limit')
          .tooltipster('enable');
      }
      else {
        this.$el
          .removeClass('over-limit')
          .tooltipster('disable');
      }
    },

    // Ideally we would not need to poll but listen for an 
    // editor-supplied change event that fires on every visible 
    // change.
    // @see https://github.com/PitonFoundation/atlas/issues/530
    // @see https://github.com/xing/wysihtml5/issues/174
    startPolling: function() {
      this.timer = setInterval($.proxy(this.updateCharacterCount, this), 250);
    },
    
    stopPolling: function() {
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
      }
    },
    
    render: function() {
      this.$el
        .html(this.getTemplate())
        .tooltipster({ content: this.options.warningText })
        .tooltipster('disable');
      if (this.options.showOnFocus) {
        this.$el.hide();
      }
      return this;
    }
  });

  /**
   * View mixin for updating a Story model's attribute and triggering
   * a save to the server.
   */
  var ModelAttributeSavingMixin = {
    /**
     * Event handler for a form element's change event
     */
    change: function(e) {
      var key = $(e.target).attr("name");
      var value = $(e.target).val();
      if ($(e.target).prop('checked')) {
        value = true;
      }
      this.saveAttr(key, value);
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
      index = _.isUndefined(index) ? this._sortedThumbnailViews.length - 1 : index; 
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
      this.model.sections.each(this.addSectionThumbnail);
      this.addCallToActionThumbnail();
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
      var numThumbnails = this._sortedThumbnailViews.length;
      var thumbnailView;

      if (numThumbnails) {
        for (i = 0; i < numThumbnails; i++) {
          thumbnailView = this._sortedThumbnailViews[i];
          this.$('.sections').append(thumbnailView.render().el);
        }

        // Enable the jQuery UI Sortable Widget on this element 
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
        title_suggestion: '',
        layout: this.model.sections.at(0).get('layout'),
        root: true,
        template_section: this.model.sections.at(0).get('template_section'),
        language: this.options.language
      });
      var postSave = function(section) {
        var thumbnailView;
        this.dispatcher.trigger("created:section", section, index);
        thumbnailView = this.addSectionThumbnail(section, index);
        thumbnailView.highlightSection(section);
        this.render();
      };
      this.model.sections.add(section, {at: index});
      section.once('sync', postSave, this);
      this.model.saveSections();
    },

    handleSort: function(evt, ui) {
      var that = this;
      var sortedIds = this.$('.sections').sortable('toArray');
      this._sortedThumbnailViews = [];
      var addView = _.bind(function(id) {
        this._sortedThumbnailViews.push(this._thumbnailViews[id]);
      }, this);
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
        this.$('.tooltip').tooltipster({
          position: 'top'
        });
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
        if (this.options.tooltip) {
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
    _.extend({}, ModelAttributeSavingMixin, {
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

      getSection: function() {
        return this.pseudoSectionId;
      }
    })
  );

  /**
   * View for editing story metadata
   */
  var StoryInfoView = Views.StoryInfoView = HandlebarsTemplateView.extend(
    _.extend({}, ModelAttributeSavingMixin, {
      id: 'story-info',

      className: 'view-container',

      options: {
        summaryEl: 'textarea[name="summary"]',
        templateSource: $('#story-info-template').html()
      },

      events: function() {
        var events = {};
        events['change ' + this.options.summaryEl] = 'change';
        return events;
      },

      workflowStep: function() {
        var view = this;

        return {
          id: 'info',
          // #579 TODO: Finalize microcopy for this
          title: gettext("Summarize your story and select a featured image"),
          text: gettext("Story Info"),
          visible: true,
          enabled: function() {
            return !_.isUndefined(view.model);
          },
          path: 'info/'
        };
      },

      initialize: function(options) {
        var thisHelp = options.help ? options.help.where({slug: 'story-information'}) : null;
        if (thisHelp && thisHelp.length) {
          this.help = thisHelp[0];
        }
        this.dispatcher = options.dispatcher;
        this.compileTemplates();

        this.featuredAssetView = new FeaturedAssetView({
          model: this.model,
          defaultImageUrl: this.options.defaultImageUrl,
          dispatcher: this.dispatcher,
          language: this.options.language
        });

        if (_.isUndefined(this.model)) {
          this.dispatcher.once("ready:story", this.setStory, this);
        }  
      },

      setStory: function(story) {
        this.model = story;
        this.render();
      },

      render: function() {
        var view = this;
        var handleChange = function () {
          // Trigger the change event on the underlying element 
          view.$(view.options.summaryEl).trigger('change');
        };

        this.$el.html(this.template(this.model.toJSON()));

        // Initialize wysihmtl5 editor.
        // We do this each time the view is rendered because wysihtml5 doesn't
        // handle being removed and re-added to the DOM very gracefully
        this.summaryEditor = new RichTextEditor(
          this.$(this.options.summaryEl).get(0),
          {
            change: handleChange
          }
        );

        // Similarly, initialize the character count view because it's a
        // pain to unbind/rebind the event bindings to the editor. :-(
        this.summaryCharCountView = new CharacterCountView({ 
          dispatcher: this.dispatcher,
          target: this.summaryEditor,
          showOnFocus: false
        });
        this.summaryEditor.$toolbar.prepend(this.summaryCharCountView.render().$el);

        this.$el.append(this.featuredAssetView.render().el);

        this.delegateEvents(); 

        return this;
      },

      onShow: function() {
        if (this.help) {
          this.dispatcher.trigger('do:set:help', this.help.toJSON());
        }
        this.featuredAssetView.onShow();
      },

      onHide: function() {
        this.dispatcher.trigger('do:clear:help');
      }
    })
  );

  /**
   * View for editing story information in the connected story builder.
   *
   * This view should be attached inside the section edit view
   *
   */
  var InlineStoryInfoEditView = Views.InlineStoryInfoEditView = HandlebarsTemplateView.extend(
    _.extend({}, ModelAttributeSavingMixin, {
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
      this.callEditor = new RichTextEditor(
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
  var SectionEditView = Views.SectionEditView = HandlebarsTemplateView.extend(
    _.extend({}, ModelAttributeSavingMixin, {
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
          // will which will trigger ``this.renderAssetViews``
          this.assets.once("sync", this.renderAssetViews, this);
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
        storybase.views.loadDeferredAssetsAndSize({ 
          assetSelector: 'iframe.sandboxed-asset',
          scope: this.$el 
        });
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
       * @param {Section} section - Section from which the asset is to be removed
       * @param {Asset} asset - Asset to be removed from the section
       * @param {object} [options]
       */
      handleDoRemoveSectionAsset: function(section, asset, options) {
        if (section == this.model) {
          this.removeAsset(asset, options);
        }
      },

      /**
      * Remove an asset from this section
      *
      * @param {Asset} asset Asset to be removed
      * @param {Object} [options] - Options for performing this operation.
      * @param {boolean} [options.removeView=undefined] - Should the view for editing the
      *   asset also be removed?
      * @param {boolean} [options.trigger=true] - Should we trigger a "remove:sectionasset"
      *   event on the event bus?
      * @param {boolean} [options.removeFromStory=false] - Should the asset be removed from
      *   the story as well?
      * @param {function} [options.success] - Callback function called on a
      *   successful removal of an asset from this section
      */
      removeAsset: function(asset, options) {
        options = options || {};
        _.defaults(options, {
          removeFromStory: false,
          trigger: true
        });
        var view = this;
        var sectionAsset = this.getSectionAsset(asset);
        sectionAsset.id = asset.id;
        sectionAsset.destroy({
          success: function(model, response) {
            if (options.removeView) {
              view.removeEditViewForAsset(asset);
            }
            view.assets.remove(asset);
            if (options.trigger) {
              view.dispatcher.trigger("remove:sectionasset", asset);
              view.dispatcher.trigger("alert", "info", "You removed an asset, but it's not gone forever. You can re-add it to a section from the asset list");
            }
            if (options.removeFromStory) {
              view.story.assets.remove(asset);
            }
            if (options.success) {
              options.success(model, asset);
            }
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
            view.assets.once("sync", view.renderAssetViews, view);
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
        var index, newIndex;
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
          index = this.model.collection.indexOf(this.model);
          if (index === 0) {
            // The how the first section. Its index is 1 because the first
            // section, with index 0, hasn't been removed yet.
            newIndex = 1;
          }
          else {
            // If this isn't the first section, make the previous section
            // the active one
            newIndex = index - 1;
          }
          // Tell other views to display the section
          this.dispatcher.trigger('select:section', this.model.collection.at(newIndex));
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
    })
  );

  var BBFFormMixin = {
    /**
    * Attempt to unify validation error handling somewhat.
    * Knows about MutexGroupedInputForms but compatible
    * with regular BBF Forms as well.
    *
    * @param {Array} errors Hash of errors provided by BBF or 
    *        hand-made.
    */
    handleValidationErrors: function(errors) {
      var view = this;

      // two ways to show errors: inline with field, or
      // on top of the form.
      var inlineErrors = {};
      var formErrors = [];

      // Function to extract an error message from the items in
      // errors._others.  Declare it here to avoid declaring an anonymous
      // function within a for loop
      var addFormError = function(error) {
        if (_.isString(error)) {
          formErrors.push(error);
        }
        else if (_.isObject(error)) {
          // The error is an object, added to _others because the key didn't
          // match a field name in the form. Just grab the first value as
          // the error message;
          for (var k in error) {
            break;
          }
          formErrors.push(error[k]);
        }
      };

      var fieldName; // Keys in errors object
      var inline; // Can a particular error be shown inline?
      var $field; // A form field's element
      var $fieldError; // A form field's error message
      var msg; // An individual error message

      // Remove any previous error-indicating UI state
      view.form.$('.bbf-error').hide();
      view.form.$('.bbf-combined-errors').remove();
      view.form.$('.nav.pills li').removeClass('error');

      for (fieldName in errors) {
        // Allow errors in "_others" to be either field-keyed error objects
        // or simple strings.
        // @see https://github.com/powmedia/backbone-forms#model-validation
        if (fieldName == '_others') {
          _.each(errors._others, addFormError); 
        }
        else {
          // if we can put in an error inline do so, otherwise throw into 
          // the combined basket up top.
          inline = false;
          $field = view.form.$('.field-' + fieldName);
          if ($field.length) {
            $fieldError = $field.find('.bbf-error');
            if ($fieldError.length) {
              inlineErrors[fieldName] = inlineErrors[fieldName] || [];
              msg = _.isString(errors[fieldName]) ? errors[fieldName] : errors[fieldName].message;
              inlineErrors[fieldName].push(msg);
              inline = true;
            }
          }

          // this error was not inline; append it to the big bucket.
          if (!inline) {
            formErrors.push(errors[fieldName].message);
          }
        }
      }

      // fill in/update elements

      _.each(inlineErrors, function(errors, fieldName) {
        var $field = view.form.$('.field-' + fieldName);

        // there may be multiple errors on a field, but we only show the first.
        $field.find('.bbf-error').html(errors[0]).slideDown('fast');

        // highlight relevant option pill, if any 
        // (for MutexGroupedInputForms)
        var optionIndex = $field.data('option-index');
        if (!_.isUndefined(optionIndex)) {
          view.form.$('.nav.pills li:eq(' + optionIndex + ')').addClass('error');
        }

      });

      if (_.size(formErrors) > 0) {
        $('<ul class="bbf-combined-errors">').prependTo(view.form.$el).slideDown('fast');
      }
      _.each(formErrors, function(error) {
        view.form.$('.bbf-combined-errors').append('<li>' + error + '</li>');
      });

    },

    /**
    * Render a thumbnail for any file inputs.
    * TODO: revisit, see if there's a way to cleanly splice this
    * into the "natural" Backbone.Forms templating pipeline.
    * 
    * Also @see storybase.forms.File.render.
    */
    renderFileFieldThumbnail: function() {
      this.form.$el.find('input[type=file]').each(function() {
        var thumbNailValue = $(this).data('file-thumbnail');
        if (thumbNailValue) {
          if (thumbNailValue == '__set__') {
            $(this).before('<div class="data-thumbnail"></div>');
          }
          else {
            $(this)
            .addClass('has-thumbnail')
            .before('<img class="file-thumbnail" src="' + $(this).data('file-thumbnail') + '">');
          }
        }
        else {
          $(this).before('<div class="not-set-thumbnail"></div>');
        }
      });
    }
  };

  var DataSetFormView = HandlebarsTemplateView.extend(_.extend({}, BBFFormMixin, {
    options: {
      templateSource: {
        'upload': $('#uploadprogress-template').html()
      }
    },

    /**
     * Get the Backbone Forms schema for the dataset form
     */
    getFormSchema: function(model) {
      var schema;
      var filename;
      
      // Start with the schema defined in either the model instance
      // or class
      if (model) {
        schema = model.schema();
      }
      else {
        schema = DataSet.prototype.schema();
      }

      // Update some labels and help text
      // TODO: Refine this microcopy
      schema.title.title = getLabelText(gettext("Dataset name"), true);
      schema.source.title = gettext("Source");
      schema.source.help = gettext("The organization or entity that created the dataset");
      if (schema.url) {
        schema.url.title = gettext("Data URL");
        schema.url.help = gettext("Enter the URL of a dataset hosted on a web site or in the cloud.");
      }
      if (schema.file) {
        schema.file.title = gettext("Data file");
        if (schema.url) {
          // Both the file and url fields should be shown, i.e. creating a new
          // model
          schema.file.help = gettext("Upload a data file from your computer.");
        }
        else {
          // Only the file field is present, i.e. editing an existing model
          filename = _.last(model.get('file').split('/'));
          schema.file.help = gettext("Current file is") + " <strong>" + filename + "</strong>. " + gettext("Change the data file by uploading a new data file from your computer.");
        }
      }

      // Add the required text to the content fields' label only if
      // one field is present, i.e. when an existing DataSet is being
      // edited
      if (!_.isUndefined(schema.url) && _.isUndefined(schema.file)) {
        schema.url.title = getLabelText(schema.url.title, true); 
      }

      return schema;
    },

    getForm: function(model, options) {
      var schema = this.getFormSchema(model);
      var contentFields = [];
      var contentFieldset;

      // HACK: There isn't a good way to show that one field OR the other
      // is required. Separate out the metadata and content fields in
      // anticipation of cleaning this up in #767
      if (schema.url) {
        contentFields.push('url');
      }
      if (schema.file) {
        contentFields.push('file');
      }

      // Editing an existing DataSet, so only one content field or the
      // other will be present
      if (contentFields.length === 1) {
        contentFieldset = contentFields;
      }
      else {
        contentFieldset = {
          fields: contentFields
        };
      }
      
      options = options || {}; 
      _.extend(options, {
        schema: schema,
        // HACK: If a model instance wasn't specified, create an empty instance 
        // to force the form to use model validation
        model: model || new DataSet(),
        fieldsets: [
          ['title', 'source'],
          contentFieldset
        ]
      });

      options.mutexGroupName = gettext('Data Source');

      return new MutexGroupedInputForm(options);
    },

    initialize: function(options) {
      this.dispatcher = options.dispatcher;
      this.form = this.getForm(this.model);
      this._formRemoved = false; // Has the form been removed during upload

      this.handleUploadProgress = _.bind(handleUploadProgress, this);

      this.compileTemplates();
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
        this.handleValidationErrors(errors);
      }
      evt.preventDefault();
      evt.stopPropagation();
    },

    handleSave: function(attrs, form) { },

    /**
     * Replace the form with an upload progress meter
     *
     * The form element is kept around so it can be reattached
     * in the case of an error.
     */
    renderUploading: function() {
      this.form.$el.detach();
      this.$el.html(this.getTemplate('upload')());
      return this;
    },

    /**
     * Reattach the form
     *
     * This is needed after the form has been detached in
     * ``renderUpload``.
     */
    reattachForm: function() {
      this.$el.empty();
      this.$el.append(this.form.$el);
      // TODO: Is this needed since we're detaching the
      // child element rather than removing it?
      this.delegateEvents();
    }
  }));

  /**
   * Form for adding a new dataset and associating it with an asset
   *
   * Events:
   *
   * "create:dataset" (model, postSaveAction) - when the dataset has been
   * succesfully saved to the server. ``model`` is the dataset that was saved. ``postSaveAction`` is the suggested
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
      DataSetFormView.prototype.initialize.apply(this, arguments);
      // Action to be taken after the form is submitted. Default is
      // 'close' which will hide this view. 'add' will show a blank
      // form allowing the user to add another
      this._postSaveAction = 'close'; 
      this.handleSave = this.addDataSet;
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
      this.$('.uploadprogress').remove();
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
          view.dispatcher.trigger('alert', 'success', "Dataset added");
          view.resetForm();
          view.trigger('create:dataset', model, view._postSaveAction);
        },
        error: function(model, response) {
          view.reattachForm(); 
          view.dispatcher.trigger('error', 'Error saving the dataset');
        }
      };

      if (attrs.file) {
        _.extend(options, {
          upload: true,
          form: $(form),
          progressHandler: this.handleUploadProgress
        });

        if (!_.isString(attrs.file)) {
          // If the file field is not a string (meaning it's a File object),
          // remove the form so we can show the upload status.
          // Otherwise, we need to keep the form around to be able to access the
          // file input element when posting the form through a hidden IFRAME
          this.renderUploading();
        }
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
      DataSetFormView.prototype.initialize.apply(this, arguments);
      this.handleSave = this.saveDataSet;
    },

    render: function() {
      this.$('.uploadprogress').remove();
      this.$el.append(
        this.form.render().$el
            .append("<input type='reset' value='" + gettext("Cancel") + "' />")
            .append("<input type='submit' name='save' value='" + gettext("Save Changes") + "' />")
      );
      this.renderFileFieldThumbnail();
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
          view.dispatcher.trigger('alert', 'success', "Dataset saved");
          view.trigger('save:dataset', model);
        },
        error: function(model, response) {
          view.reattachForm(); 
          view.dispatcher.trigger('error', 'Error saving the dataset');
        }
      };

      if (!_.isUndefined(attrs.file)) {
        _.extend(options, {
          upload: true,
          form: $(form),
          progressHandler: this.handleUploadProgress
        });

        if (!_.isString(attrs.file)) {
          // If the file field is not a string (meaning it's a File object),
          // remove the form so we can show the upload status.
          // Otherwise, we need to keep the form around to be able to access the
          // file input element when posting the form through a hidden IFRAME
          this.renderUploading();
        }
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
        // Hide the add dataset subview and show the
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

  /**
   * Creates a new state obect for SectionAssetEditView.
   * @constructor
   *
   * @param {SectionAssetEditView} view
   */ 
  var SectionAssetEditViewState = function(view) {
    this.view = view;
    this.initialize();
  };

  // Set up default methods and properties for a SectionAssetEditView state
  _.extend(SectionAssetEditViewState.prototype, HandlebarsTemplateMixin, {
    options: {},

    /**
     * Initialize the state.
     *
     * Called from the constructor.
     */
    initialize: function() {
      this.compileTemplates();
    },

    /**
     * Get template context used in SectionAssetEditView.render
     * @returns {object} - Template context
     */
    context: function() { 
      return {};
    },

    /**
     * Adds state-specific CSS classes to view element.
     */
    addClass: function() {
      this.view.$el.addClass(this.name);
    },

    /**
     * Remove state-specific CSS classes to view element.
     */
    removeClass: function() {
      this.view.$el.removeClass(this.name);
    },

    /**
     * Hook called when changing to this state.
     */
    enter: function() {},

    /**
     * Hook before changing away from this state.
     */
    exit: function() {
      this.removeClass();
    },

    /**
     * Hook called when view is rendered in this state.
     */
    render: function() {
      this.addClass();
    },

    /**
     * Returns asset type specific help for the state
     *
     * @param {string|undefined} assetType - String representing the type of
     *   asset of the view's model, or undefined.
     *
     * @returns {string} Help for this particular state and asset type,
     *   the state itself, or an empty string.
     */
    help: function(assetType) {
      var templateName = assetType ? assetType + '-help' : 'help';
      var template = this.getTemplate(templateName);

      if (template) {
        return template();
      }

      return '';
    }
  });

  // HACK: Use Backbone's extend function for inheritance of
  // our class. It's not exported explicitly, but assigned to
  // Backbone.View.extend, Backbone.Model.extend, etc.
  SectionAssetEditViewState.extend = Backbone.View.extend;

  var DisplayState = SectionAssetEditViewState.extend({
    name: 'display',

    options: {
      templateSource: {
        __main: $('#section-asset-display-template').html(),
        'image-help': $('#image-display-help-template').html()
      }
    },

    context: function() {
      // Set context variable to toggle display of icon to edit data
      return {
        acceptsData: this.view.model.acceptsData()
      };
    },

    render: function() {
      if (this.view.$el.is(':visible')) {
        storybase.views.sizeAssetsOnLoad({
          assetSelector: 'iframe.sandboxed-asset',
          scope: this.view.$el
        });
      }
      else {
        storybase.views.deferSrcLoad({
          selector: 'iframe.sandboxed-asset',
          scope: this.view.$el
        });
      }
    }
  });

  var EditState = SectionAssetEditViewState.extend({
    name: 'edit',

    options: {
      templateSource: {
        __main: $('#section-asset-edit-template').html(),
        'image-help': $('#image-edit-help-template').html()
      }
    },

    enter: function() {
      var view = this.view;
      // Save the model's new state. We need to remember if the model was new
      // before any auto-saving
      view.modelNew = view.model.isNew();


      // Set autosaved flag to false as the model has not yet been autosaved
      view.modelAutoSaved = false;
      if (!view.modelNew) {
        // Save the model attributes in case the user cancels editing and we
        // need to revert an auto-saved version
        view.oldModelAttributes = _.clone(view.model.attributes); 
      }
    },

    context: function() {
      return {
        action: this.view.model.isNew() ? gettext('add') : gettext('edit')
      };
    },

    render: function() {
      var view = this.view;
      var $wrapperEl = view.$(view.options.wrapperEl);

      // Initialize the form
      view.initializeForm();

      view.form.render().$el.append('<input type="reset" value="' + gettext("Cancel") + '" />').append('<input type="submit" value="' + gettext("Save Changes") + '" />');

      if (view.model.get('type') == 'text') {
        // Text asset.

        // Hide the label of the field since there's only one field
        view.form.fields.body.$('label').hide();

        // Make sure that the textarea element is visible, if it was
        // previously hidden by the rich text editor and not revealed.  
        // This occurs when the "Cancel" button is clicked as the 
        // editor never re-reveals the element before being destroyed
        // When a new editor is initialized, it copies the old 
        // ``display: none`` style from the textarea, causing the iframe
        // to be hidden.
        view.form.fields.body.editor.$el.show();

        // Create a rich-text editor for the 'body' field 
        view.bodyEditor = new RichTextEditor(
          view.form.fields.body.editor.el,
          undefined,
          {
            grow: true,
            toggleToolbar: false
          }
        );

        // The Backbone Forms text "editor" view listens to the keyup event, which
        // never gets passed to the underlying textarea by wysihtml5.
        //
        // Watch for the keyup event in the the wysihtml5 editor and trigger
        // it on the underlying Backbone Forms editor.
        //
        // We do this to make event binding more agnostic to the particular
        // rich text editor.  We may move away from wysihtml5, but we'll
        // probably stick with Backbone Forms (or at least use something
        // that uses Backbone's events)
        view.bodyEditor.on('load', function() {
          var editor = this;

          $(editor.composer.element).on('keyup', function() {
            // wysihtml5 doesn't sync the composer and textarea
            // immediately. Force a sync so the form view will
            // detect that the textarea's value has changed
            editor.synchronizer.sync(true); 
            view.form.fields.body.editor.$el.trigger('keyup');
          });
        });

        view.form.on('body:change', view.autosave, view); 
      }

      view.renderFileFieldThumbnail();
          
      $wrapperEl.append(view.form.el);
    }
  });

  var UploadState = SectionAssetEditViewState.extend({
    name: 'upload',

    options: {
      templateSource: $('#asset-uploadprogress-template').html()
    }
  });

  var EditDataState = SectionAssetEditViewState.extend({
    name: 'editData',

    render: function() {
      this.view.$el.append(this.view.datasetListView.render().el);
    }
  });

  var SelectState = SectionAssetEditViewState.extend({
    name: 'select',

    options: {
      templateSource: {
        __main: $('#section-asset-select-type-template').html(),
        help: $('#select-help-template').html()
      }
    },

    context: function() {
      return {
        assetTypes: this.view.getAssetTypes(),
        help: this.view.options.help
      };
    },

    render: function() {
      var $wrapperEl = this.view.$(this.view.options.wrapperEl);
      // The accept option needs to match the class on the items in
      // the UnusedAssetView list
      $wrapperEl.droppable({ accept: ".unused-asset" });
      this.addClass();
    }
  });

  var SyncState = SectionAssetEditViewState.extend({
    name: 'sync',

    options: {
      templateSource: $('#section-asset-sync-template').html()
    }
  });

  var SectionAssetEditView = Views.SectionAssetEditView = HandlebarsTemplateView.extend(
    _.extend({}, BBFFormMixin, {
      tagName: 'div',

      className: 'edit-section-asset',

      options: {
        wrapperEl: '.wrapper',
        templateSource: {
          'audio-help': $('#audio-help-template').html(),
          'chart-help': $('#chart-help-template').html(),
          'image-help': $('#image-help-template').html(),
          'image-new-help': $('#image-new-help-template').html(),
          'map-help': $('#map-help-template').html(),
          'quotation-help': $('#quotation-help-template').html(),
          'table-help': $('#table-help-template').html(),
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
        this.states = {
          select: new SelectState(this),
          display: new DisplayState(this),
          edit: new EditState(this),
          editData: new EditDataState(this),
          sync: new SyncState(this),
          upload: new UploadState(this)
        };
        this.handleUploadProgress = _.bind(handleUploadProgress, this);
        this.bindModelEvents();
        this.setInitialState();
      },

      bindModelEvents: function() {
        this.model.on("remove", this.handleModelRemove, this);
        if (this.model.isNew()) {
          this.model.once("sync", this.initializeDataViews, this);
        }
      },

      unbindModelEvents: function() {
        this.model.off("remove", this.handleModelRemove, this);
        this.model.off("sync", this.initializeDataViews, this);
      },

      unbindBusEvents: function() {
        this.dispatcher.off('close:drawer', this.revertHelp, this);
      },

      /**
       * Cleanup the view.
       */
      close: function() {
        this.remove();
        this.undelegateEvents();
        this.unbind();
        this.unbindModelEvents();
        this.unbindBusEvents();
      },

      /**
       * Get the Backbone Forms schema for the asset form
       */
      getFormSchema: function(model) {
        var schema = _.result(this.model, 'schema');
        var type = this.model.get('type');
        var num_elements = _.size(_.pick(schema, 'image', 'body', 'url')); 
        var prefix = num_elements > 1 ? gettext("or") + ", " : "";

        if (schema.url) {
          schema.url.title = capfirst(gettext("enter") + " " + type + " " + gettext("URL"));
        }
        if (schema.image) {
          if (!model.isNew()) {
            schema.image.title = capfirst(gettext('replace image file'));
            var imagePath = model.get('image');
            if (imagePath && _.isString(imagePath)) {
              schema.image.help = capfirst(gettext('current image is <strong>' + _.last(imagePath.split('/')) + '</strong>.'));
              schema.image.help += ' ' + capfirst(gettext("change this by uploading a new image from your computer."));
            }
          }
          else {
            schema.image.title = capfirst(gettext('upload an image'));
            schema.image.help = capfirst(gettext('choose a file from your computer.'));
          }
        }
        if (schema.body) {
          if (type === 'text') {
            schema.body.template = _.template('\
                <li class="bbf-field field-{{key}}">\
                  <div class="bbf-editor">{{editor}}</div>\
                  <div class="bbf-help">{{help}}</div>\
                </li>\
              '
              );
          }
          else if (type === 'quotation') {
            schema.body.title = capfirst(gettext("enter the quotation text"));
          }
          else {
            schema.body.title = capfirst(gettext("paste embed code for the") + " " + type);
          }
        }

        return schema;
      },

      /**
       * Set the view's form property based on the current state of the model.
       */
      initializeForm: function() {
        this.form = new MutexGroupedInputForm({
          schema: this.getFormSchema(this.model),
          model: this.model,
          mutexGroupName: capfirst(this.model.get('type') || '') + ' ' + capfirst(gettext('source'))
        });
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
       * Event handler for adding a new dataset to the asset
       */
      handleDataSetListClose: function(refresh) {
        var view;
        if (refresh) {
          // The user wants to close the add dataset form
          view = this;
          this.setState('sync').render();
          // Refresh the asset model to get the updated rendered dataset
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
       * Initialize subviews for related datasets
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
            // There's no dataset list view - create one
            this.datasetListView = new AssetDataSetListView({
              model: this.model,
              dispatcher: this.dispatcher
            });
            // If the cancel button is clicked inside the dataset
            // list view, or if a dataset has been added and (without
            // choosing to add another) hide the dataset list view and show the display
            // view
            this.datasetListView.on('close', this.handleDataSetListClose, this);
          }
          else {
            // There's already a dataset list view - reuse it
            this.datasetListView.setModel(this.model);
          }
        }
      },

      render: function() {
        var context = this.state.context(); 
        var template = this.state.getTemplate();
        var $wrapperEl;

        context.model = this.model.toJSON();

        if (template) {
          this.$el.html(template(context));
        }
        else {
          this.$el.empty();
        }

        $wrapperEl = this.$(this.options.wrapperEl);

        this.state.render();

        return this;
      },

      setInitialState: function() {
        if (!this.model.isNew()) {
          this.state = this.states.display;
        }
        else {
          this.state = this.states.select;
        }
      },

      setState: function(state) {
        this.state.exit();
        this.state = this.states[state];
        this.state.enter();
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
        this.setState('edit').render();
      },

      /**
       * Event handler for canceling form interaction
       */
      cancel: function(e) {
        e.preventDefault();
        this.cancelAutosave();
        var nextState = this.modelNew ? 'select' : 'display';
        if (this.modelAutoSaved){
          if (this.modelNew) {
            // Model was auto-saved. Remove it
            this.dispatcher.trigger('do:remove:sectionasset', this.section,
              this.model,
              {
                removeFromStory: true,
                trigger: false,
                success: function(sectionAsset, asset) {
                  // Destroy the asset only after the asset has already been 
                  // disassociated with the section. Otherwise, there's 
                  // a race condition on the server
                  asset.destroy();
                }
              }
            ); 
          }
          else {
            // Asset was autosaved, restore the old attributes
            this.saveModel(this.oldModelAttributes);
          }
          return;
        }

        this.setState(nextState);
        this.render();
      },

      /**
       * Save the asset model to the server.
       *
       * This method mostly handles initializing the callbacks and options for 
       * Asset.save()
       *
       * @param {Object} attributes - Model attributes to be passed to
       *     Asset.save()
       * @param {Object} [options] - Options for altering save timing and
       *     side effects.
       * @param {boolean} [options.changeState=true] - Change the state of this view 
       *     and re-render after a successful save. 
       * @param {number} [options.delay=null] - Delay saving by this number of
       *     milliseconds.
       * @param {function} [success] - Callback function called after model
       *     is successfully saved.
       */
      saveModel: function(attributes, options) {
        options = options || {};
        _.defaults(options, {
          changeState: true,
          delay: null
        });
        var view = this;
        // Save the model's original new state to decide
        // whether to send a signal later
        var isNew = this.model.isNew();
        var storyLicense = this.story.get('license');
        var saveOptions;

        // If this is the initial save and the story has a license
        // defined and the asset has no explicit license defined, set the
        // asset license to that of the story.
        if (isNew && _.isUndefined(attributes.license) && storyLicense) {
          attributes.license = storyLicense;
        }

        // Initialize callbacks for saving the model
        saveOptions = {
          success: function(model) {
            if (options.changeState) {
              view.setState('display').render();
            }

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

            if (options.success) {
              options.success(model);
            }
          },
          error: function(model, xhr) {
            // If we've switched to the upload progress view, switch back to the
            // form
            if (view.state.name === 'upload') {
              view.setState('edit').render();
            }
            view.dispatcher.trigger('error', xhr.responseText || 'error saving the asset');
          }
        };

        if (attributes.image && !_.isUndefined(this.form.fields.image) && !attributes.url) {
          // A new file is being uploaded, provide some
          // additional options to Story.save()
          _.extend(saveOptions, {
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
        else if (_.has(attributes, 'image')) {
          // The attributes have a ``image`` key, but it's undefined.
          // This means we're not updating the image field.  Just throw away
          // the undefined file attribute so we keep whatever value is in the
          // model
          delete attributes.image;
        }

        if (options.delay) {
          this.saveTimeoutID = setTimeout(function() {
            view.model.save(attributes, saveOptions);
          }, options.delay);
        }
        else {
          this.model.save(attributes, saveOptions); 
        }
      },

      /**
       * Cancel a pending autosave of the model.
       *
       * This should be called before initiating an explicit save to avoid
       * making multiple requests.
       */
      cancelAutosave: function() {
        // Do we need to do a more specific check of
        // this.saveTimeoutID here?  Can we assume that if it's
        // set it will always be truthy?
        if (this.saveTimeoutID) {
          clearTimeout(this.saveTimeoutID);
          this.saveTimeoutID = null;
        }
      },

      /**
       * Callback for initiating a save of the model
       *
       * This is meant to be bound to a Backbone Forms field change event.
       *
       * @param {Backbone.Form} [form=this.form] - Backbone Form instance
       *   containing fields that can be used to update this view's model.
       *
       */
      autosave: function(form) {
        var view = this;
        form = form || this.form;

        // If there's a pending save, squash it. We only want to save after
        // things stop changing for a second or so
        this.cancelAutosave();

        // Save the asset, but delay saving to give the user
        // some time to do an explicit save or cancel using the
        // form buttons.
        this.saveModel(form.getValue(), {
          changeState: false,
          delay: 2000,
          success: function() {
            view.modelAutoSaved = true;
          }
        });
      },

      /**
       * Event handler for submitting form
       */
      processForm: function(e) {
        e.preventDefault();
        this.cancelAutosave();

        var errors = this.form.validate();
        var data;
        var view = this;

        if (!errors) {
          data = this.form.getValue();
          this.saveModel(data);
        }
        else {
          this.handleValidationErrors(errors);
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
      
      /**
       * @param {String} type - The asset type.
       */
      getAssetTypeHelp: function(type) {
        var help;
        var template;

        // See if there's help for creating a new asset
        if (this.model.isNew()) {
          template = this.getTemplate(type + '-new' + '-help');
          if (template) {
            return template();
          }
        }

        // See if there's state-specific help for this type 
        help = this.state.help(type);
        if (help) {
          return help;
        }

        // See if there's a template defined for any/every state
        template = this.getTemplate(type + '-help');
        if (template) {
          return template();
        }

        return gettext("Select an asset type.");
      },

      /**
       * Show help 
       */
      showHelp: function(evt) {
        var help = _.extend({
          title: "",
          body: ""
        }, this.options.help);
        // Try to get state-specific, type agnostic help
        var assetHelp = this.state.help();
        // Try to get type-specific help
        if (!assetHelp) {
          assetHelp = this.getAssetTypeHelp(this.model.get('type'));
        }
        help.body += assetHelp;
        this.dispatcher.trigger('do:show:help', help, {remember: true});
        // When the drawer is closed, revert to the previous help item
        this.dispatcher.once('close:drawer', this.revertHelp, this); 
      },

      revertHelp: function() {
        this.dispatcher.trigger('do:pop:help');
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

  var TaxonomyView = Views.TaxonomyView = HandlebarsTemplateView.extend(
    _.extend({}, {
      id: 'share-taxonomy',

      className: 'view-container',

      options: {
        templateSource: $('#share-taxonomy-template').html()
      },

      workflowStep: function() {
        return {
          id: 'tag',
          title: gettext("Label your story with topics and places so that people can easily discover it on Floodlight"),
          text: gettext('Tag'),
          visible: true,
          enabled: _.bind(storySaved, this), 
          path: 'tag/'
        };
      },

      initialize: function() {
        this.dispatcher = this.options.dispatcher;
        this.compileTemplates();
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

    initialize: function(options) {
      this.dispatcher = options.dispatcher;
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

    close: function() {
      this.dispatcher.off("ready:story", this.setStory, this);
      this.dispatcher.off("select:license", this.getLicenseHtml, this);
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
        that._licenseHtml = data.html;
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

    close: function() {
      this.dispatcher.off("ready:story", this.setStory, this);
      this.licenseDisplayView.close();
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
        var values = this.form.getValue();
        this.dispatcher.trigger("select:license");
        // Update the form values
        _.each(values, function(value, attr) {
          this.form.setValue(attr, value);
        }, this);
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

    initialize: function(options) {
      this.compileTemplates();
      this.dispatcher = options.dispatcher;
      this.initListeners();
    }
  });

  var PublishView = Views.PublishView = PublishViewBase.extend(
    _.extend({}, {
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

      workflowStep: function() {
        return {
          id: 'publish',
          title: gettext("Post your story to Floodlight and your social networks"),
          text: gettext('Publish/Share'),
          visible: true,
          enabled: _.bind(storySaved, this), 
          path: 'publish/'
        };
      },

      initListeners: function() {
        if (_.isUndefined(this.model)) {
          this.dispatcher.once("ready:story", this.setStory, this);
        }
        else {
          this.listenTo(this.model, "change:status", this.handleChangeStatus);
        }
      },

      initialize: function(options) {
        PublishViewBase.prototype.initialize.apply(this, arguments);

        this._sharingWidgetInitialized = false;
        this.licenseView = new LicenseView({
          model: this.model,
          dispatcher: this.dispatcher,
          licenseEndpoint: this.options.licenseEndpoint,
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
        this.subviews = [this.licenseView, this.buttonView];
      },

      close: function() {
        this.dispatcher.off("ready:story", this.setStory, this);
        this.stopListening(this.model, "change:status", this.handleChangeStatus);
        this.licenseView.close();
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
          // /stories/{{story_id}}/share-popup/ endpoint will fail
          this.model.once("sync", this.initSharingWidget, this);
          return;
        }
        this.$('.storybase-share-button').storybaseShare();
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
          storyId: this.model ? this.model.id : '',
          storyUrl: this.model ? this.model.get('url') : ''
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
        this.delegateEvents();
        return this;
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

    initialize: function(options) {
      PublishViewBase.prototype.initialize.apply(this, arguments);
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
    },

    onShow: function() {
      this.delegateEvents();
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
      this.handleUploadProgress = _.bind(handleUploadProgress, this);
    },

    enabled: true,

    initListeners: function() {
      this.dispatcher.once('ready:story', this.setStory, this);
    },

    getFormSchema: function(model) {
      var schema = _.result(model, 'schema');

      if (schema.url) {
        schema.url.title = capfirst(gettext("enter the featured image URL"));
      }
      if (schema.image) {
        schema.image.title = capfirst(gettext("select the featured image from your own computer"));
      }

      return schema;
    },

    initializeForm: function() {
      var model = new this.options.assetModelClass({
          language: this.options.language,
          type: 'image'
      });

      if (this.form) {
        // If there was a previous version of the form, remove it from the 
        // DOM and detach event listeners 
        this.form.remove();
      }
      // Create a new form with a new bound model instance
      this.form = new Backbone.Form({
        schema: this.getFormSchema(model),
        model: model
      });
      this.form.render();
      // Set a flag to tell render() that the form element
      // needs to be appended to the view element
      this._appendForm = true;
      return this;
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
      else {
        this.$el.empty();
      }

      if (this._appendForm) {
        this.form.$el.append('<input type="reset" value="' + gettext("Cancel") + '" />').append('<input type="submit" value="' + gettext("Save Changes") + '" />');
        this.$el.append(this.form.el);
        this._appendForm = false;
      }

      return this;
    },

    onShow: function() {
      this.delegateEvents();
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
        this.form.$('.bbf-combined-errors').remove();
        if (!_.isUndefined(errors._others)) {
          this.form.$el.prepend('<ul class="bbf-combined-errors">');
          _.each(errors._others, function(msg) {
            this.form.$('.bbf-combined-errors').append('<li>' + msg + '</li>');
          }, this);
        }
      }
    },

    /**
     * Set the featured asset on the story and add the
     * asset to its collection of assets.
     */
    setFeaturedAsset: function(model) {
      this.model.setFeaturedAsset(model);
      this.model.assets.add(model);
    },

    saveModel: function(model) {
      var view = this;
      var image = model.get('image');
      var options = {
        error: function(model) {
          view.dispatcher.trigger('error', gettext('Error saving the featured image'));
        },
        success: function(model, response) {
          if (view.model.isNew()) {
            // Story is unsaved.  Save it before
            // setting the featured asset.
            view.model.once('sync', function() {
              view.setFeaturedAsset(model);
            });
            view.dispatcher.trigger('do:save:story');
          }
          else {
            // Story has been previously saved.  Just set the
            // asset.
            view.setFeaturedAsset(model);
          }
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
        'nav-item': '<li{{#if class}} class="{{class}}"{{/if}}><a href="#{{viewId}}">{{title}}</a></li>'
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
        if (view.onShow) {
          view.onShow();
        }
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

    /**
     * Set the story's initial featured asset when an image asset is added.
     *
     * This is meant to be added as an event listener for the ``add`` event
     * on the view's ``model.assets`` collection.
     */
    handleAddAsset: function(asset) {
      if (asset.get('type') === 'image') {
        if (asset.get('content')) {
          // The content attribute will only be set when an asset has
          // synced with the server.  So, we can go ahead and set this
          // asset as the story's featured asset.
          this.model.setFeaturedAsset(asset);
        }
        else {
          // Wait until the file upload has completed and the asset model has
          // synced before setting it as the featured asset. This works around
          // a race condition where FeaturedAssetDisplayView would render
          // before the asset attributes were updated.
          asset.once('change:content', function(asset) {
            this.model.setFeaturedAsset(asset);    
          }, this);
        }
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
      'click .unpublish': 'handleUnpublish'
    },

    options: {
      templateSource: $('#published-buttons-template').html()
    },

    initListeners: function() {
      // If the model isn't defined at initialization (usually when creating
      // a new story), wire up a listener to set it when the story is ready.
      if (_.isUndefined(this.model)) {
        this.dispatcher.once("ready:story", this.setStory, this);
      }
      else {
        this.listenTo(this.model, "change:status", this.handleChangeStatus);
        // When the viewer URL is set, (re)render this view
        this.listenTo(this.model, "change:viewer_url", this.render);
      }
    },

    initialize: function(options) {
      PublishViewBase.prototype.initialize.apply(this, arguments);
    },

    handleChangeStatus: function(story, statusVal, options) {
      this.toggle();
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
      this.$el.html(this.template({
        url: this.model ? this.model.get('viewer_url') : ''
      }));

      this.toggle();

      return this;
    },

    toggle: function() {
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

    initialize: function(options) {
      PublishViewBase.prototype.initialize.apply(this, arguments);
      // Object to manage alerts emitted by this view, so we can close them.
      // Keys are alert IDs, as passed as the ``alertId`` property of the
      // options when triggering the ``alert`` event.  Values are a boolean
      // or an ``AlertView`` instance.
      this._alerts = {};
    },

    initListeners: function() {
      if (_.isUndefined(this.model)) {
        this.dispatcher.once('ready:story', this.setStory, this);
      }
      else {
        this.listenTo(this.model, 'change:status', this.handleChangeStatus);
      }

      this.dispatcher.on('show:alert', this.handleAlert, this);
    },

    handleChangeStatus: function(story, statusVal, options) {
      if (statusVal !== 'published') {
        this.render();
      }
    },

    /**
     * Event handler for a ``show:alert`` event.
     */
    handleAlert: function(level, msg, view) {
      if (view.alertId && this._alerts[view.alertId]) {
        this._alerts[view.alertId] = view;
      }
    },

    /**
     * Clear all alerts created by this view.
     */
    clearAlerts: function() {
      var cleared = [];

      // Close all alert views
      _.each(this._alerts, function(view, alertId) {
        if (view.close) {
          view.close();
          cleared.push(alertId);
        }
      }, this);

      // Remove the closed alert views from our map of known alerts
      _.each(cleared, function(alertId) {
        delete this._alerts[alertId];
      }, this);
    },

    /**
     * Returns an error messasge describing missing required story components.
     *
     * @param {object} validation Validation error object returned by
     *   Story.validateStory().
     */
    _requiredComponentMissingMsg: function(validation) {
      if (validation.errors && validation.errors.title) {
        return gettext("You haven't given your story a <strong>title</strong>. You'll need to do this before you can publish."); 
      }

      // Should never get here, but just add a default case
      // in case we're lazy
      return gettext("Your story is missing a required component");
    },

    // Map of suggested fields to human readable strings
    _suggestedFieldMessages: {
      byline: gettext('author information'),
      featuredAsset: gettext('featured image')
    },

    /**
     * Returns a warning messasge describing missing required story components.
     *
     * @param {object} validation Validation error object returned by
     *   Story.validateStory().
     */
    _suggestedComponentMissingMsg: function(validation) {
      if (validation.warnings) {
        var msg = gettext("Your story is missing these suggested components") + ": ";
        msg += _.map(_.keys(validation.warnings), function(field) {
          var fieldString = this._suggestedFieldMessages[field] ? this._suggestedFieldMessages[field] : field;
          return "<strong>" + fieldString + "</strong>";
        }, this)
        .join(", ");

        msg += ". " + gettext("Your story was still published, but you should add them.");

        return msg;
      }

      return gettext("Your story is missing some suggested components");
    },

    handlePublish: function(evt) {
      var validation = this.model.validateStory();
      
      this.clearAlerts();

      if (_.isUndefined(validation) || _.isUndefined(validation.errors)) {
        // Validation succeeded
        var view = this;
        var triggerPublished = function(model, response) {
          view.dispatcher.trigger('alert', 'success', 'Story published');
        };
        var triggerError = function(model, response) {
          view.dispatcher.trigger('error', "Error publishing story");
        };
        this.model.save({'status': 'published'}, {
          success: triggerPublished, 
          error: triggerError 
        });
        this.render();

        // If there were validation warnings, show an alert
        if (!_.isUndefined(validation) && validation.warnings) {
          this._alerts['publish-validation-warnings'] = true;
          this.dispatcher.trigger('alert', 'info',
            this._suggestedComponentMissingMsg(validation),
            {timeout: null, sticky: true, alertId: 'publish-validation-warnings'}
          );
        }
      }
      else {
        // Validation failed, show an alert
        if (validation.errors) {
          this._alerts['publish-validation-errors'] = true;
          this.dispatcher.trigger('alert', 'error',
            this._requiredComponentMissingMsg(validation),
            {timeout: null, sticky: true, alertId: 'publish-validation-errors'}
          );
        }
      }

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

      this.delegateEvents();

      return this;
    }
  });
})(window, $, _, Backbone, Modernizr, wysihtml5, guiders, storybase);
