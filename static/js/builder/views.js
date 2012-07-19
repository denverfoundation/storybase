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
    'click .assets': 'toggleAssetList' 
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

  toggleAssetList: function(evt) {
    evt.preventDefault();
    this.dispatcher.trigger("toggle:assetlist");
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

  templateSource: $('#builder-template').html(),

  initialize: function() {
    var that = this;

    this.dispatcher = this.options.dispatcher;

    if (_.isUndefined(this.model)) {
      // Create the story instance
      this.model = new storybase.models.Story({
        title: ""
      });
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
    this.$el.prepend(this.unusedAssetView.render().$el.hide());
    this.$el.prepend(this.lastSavedView.render().el);
    if (this._thumbnailViews.length) {
      _.each(this._thumbnailViews, function(view) {
        that.$(".sections").append(view.render().el);
        //that.$el.prepend(view.editView.render().el);
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
    console.info("Saving story");
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
    thumbnailView.editView.$el.show();
  },

  toggleAssetList: function() {
    this.unusedAssetView.$el.toggle(); 
  }
});

storybase.builder.views.LastSavedView = Backbone.View.extend({
  tagName: 'div',

  className: 'last-saved',

  initialize: function() {
    console.debug(this.options.lastSaved);
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
    this.setState('edit');
    this.render();
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
