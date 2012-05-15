/**
 * Views for the story explorer Backbone application
 */
Namespace('storybase.explorer');

storybase.explorer.views.ExplorerApp = Backbone.View.extend({
  el: $('#explorer'),

  templateSource: $('#explorer-template').html(),

  defaults: {
    bufferPx: 40,
    pixelsFromListToBottom: undefined
  },

  events: {
    "click .select-tile-view": "selectTile",
    "click .select-list-view": "selectList",
    "change #filters select": "changeFilters"
  },

  initialize: function() {
    var that = this;
    _.defaults(this.options, this.defaults);
    this.selectedFilters = {}; 
    // Flag to keep from re-fetching the same page of items when we're 
    // scrolled near the bottom of the window, but the new items haven't yet
    // loaded
    this.isDuringAjax = false; 
    this.stories = new storybase.collections.Stories;
    this.reset(this.options.storyData);
    this.template = Handlebars.compile(this.templateSource);
    this.filterView = new storybase.explorer.views.Filters({
      topics: this.options.storyData.topics,
      organizations: this.options.storyData.organizations,
      projects: this.options.storyData.projecs,
      languages: this.options.storyData.languages
    });
    this.storyListView = new storybase.explorer.views.StoryList({
      stories: this.stories
    });

    $(window).bind('scroll', function(ev) {
      that.scrollWindow(ev);
    });
  },

  reset: function(data) {
    this.nextUri = data.meta.next;
    this.resourceUri = data.meta.resource_uri;
    this.stories.reset(data.objects);
  },

  render: function() {
    var opts = this.options;
    var context = {
    };
    this.$el.html(this.template(context));
    this.filterView.render();
    this.$el.prepend(this.filterView.el);
    this.filterView.setInitialProperties();
    this.$el.append(this.storyListView.el);
    this.selectTile();
    this.storyListView.render();
    // Distance from story list to bottom
    // Computed as: height of the document - top offset of story list container
    // - outer height of story list container
    this.options.pixelsFromListToBottom = $(document).height() - this.storyListView.$el.offset().top - this.storyListView.$el.outerHeight(); 
    return this;
  },

  selectTile: function(e) {
    this.storyListView.tile();
    return false;
  },

  selectList: function(e) {
    this.storyListView.list();
    return false;
  },

  /** 
   * Check if the window has been scrolled to the bottom.
   */
  _nearbottom: function() {
    var opts = this.options;
    var pixelsFromWindowBottomToBottom = 0 + $(document).height() - $(window).scrollTop() - $(window).height();
    return (pixelsFromWindowBottomToBottom - opts.bufferPx < opts.pixelsFromListToBottom);
  },

  getMoreStories: function() {
      var that = this;
      if (this.nextUri) {
        this.isDuringAjax = true;
        $.getJSON(this.nextUri, function(data) {
          that.nextUri = data.meta.next;
          _.each(data.objects, function(storyJSON) {
            var story = new storybase.models.Story(storyJSON);
            that.stories.push(story);
            that.storyListView.appendStory(story);
          });
          that.isDuringAjax = false;
        });
      }
      else {
        console.debug('No more stories');
      }
  },

  scrollWindow: function(e) {
    if (this._nearbottom() && !this.isDuringAjax) {
      this.getMoreStories();
      this.storyListView.render();
    }
  },

  /**
   * Get the resource URI including a query string based on the filters
   */
  getFilterUri: function() {
    var filterUri = this.resourceUri;
    var filterStrings = [];
    _.each(this.selectedFilters, function(value, key, list) {
      if (!!value && value.length > 0) {
        var filterString = key + "=";
        var values = [];
        _.each(value, function(element, index, list) {
          values.push(element);
        });
        filterString += values.join(",");
        filterStrings.push(filterString);
      }
    });
    filterUri = filterStrings.length > 0 ? filterUri + '?' : filterUri;
    filterUri += filterStrings.join("&");
    return filterUri;
  },

  setFilter : function(name, value) {
    if (typeof value === "string") {
      this.selectedFilters[name] = [value];
    }
    else {
      this.selectedFilters[name] = value;
    }
  },

  changeFilters: function(ev) {
    var that = this;
    var name = ev.currentTarget.name;
    var value =  $(ev.currentTarget).val();
    var storyData;
    this.setFilter(name, value);
    $.getJSON(this.getFilterUri(), function(data) {
      console.debug(data);
      that.reset(data);
      that.storyListView.reset(that.stories);
      that.storyListView.render();
      that.filterView.reset({
        topics: data.topics,
        organizations: data.organizations,
        projects: data.projects,
        languages: data.languages,
        selected: that.selectedFilters
      });
      that.filterView.render();
    });
  }
});

storybase.explorer.views.Filters = Backbone.View.extend({
  tagName: 'div',

  id: 'filters',

  templateSource: $('#filters-template').html(),

  initialize: function() {
    var that = this;
    this.initialOffset = null;
    this.template = Handlebars.compile(this.templateSource);

    // Manually bind window events 
    $(window).bind('scroll', function(ev) {
      that.scrollWindow(ev);
    });

    $(window).bind('resize', function(ev) {
      that.resizeWindow(ev);
    });
  },


  /**
   * Build a context object for passing to the template
   *
   * Sets a selected attribute on filter options that should be selected.
   */
  buildContext: function() {
    var context = {
      topics: this.options.topics,
      organizations: this.options.organizations,
      projects: this.options.projects,
      languages: this.options.languages,
    };
    if (!(typeof this.options.selected === "undefined")) {
      _.each(this.options.selected, function(selected, filter, list) {
        _.each(selected, function(element, index, list) {
          var option = _.find(context[filter], function(obj) {
            return obj.id == element;
          });
          if(!(typeof option === "undefined")) {
            option.selected = true;
          }
        });
      });
    }

    return context;
  },

  render: function() {
    var context = this.buildContext();
    this.$el.html(this.template(context));
    this.$('select').select2({
      allowClear: true
    });
    return this;
  },

  reset: function(options) {
    _.extend(this.options, options);
  },

  setInitialProperties: function() {
    this.initialOffset = this.$el.offset(); 
    this.initialWidth = this.$el.width();
  },

  /**
   * Event handler for window resize
   *
   * When the window is resized, adjust the width of the filter container.
   * It won't automatically resize relative to its parent element when its
   * position is fixed.
   */
  resizeWindow: function(ev) {
    var parentWidth = this.$el.parents().width();
    var newWidth = parentWidth - (this.$el.outerWidth() - this.$el.width()); 
    this.initialWidth = newWidth; 
    this.$el.width(newWidth);
  },

  /*
   * Event handler for window scroll
   *
   * Check to see if the filters would have scroll off screen and stick them 
   * to the top of the screen so they're always visible
   */
  scrollWindow: function(ev) {
    var scrollTop = $(window).scrollTop();
    if (scrollTop > this.initialOffset.top) {
      this.$el.addClass('sticky');
      this.$el.width(this.initialWidth);
    }
    else {
      this.$el.removeClass('sticky');
    }
  }
});

storybase.explorer.views.StoryList = Backbone.View.extend({
  tagName: 'ul',

  id: 'story-list',

  templateSource: $('#story-template').html(),

  initialize: function() {
    this.newStories = this.options.stories.toArray();
    this.template = Handlebars.compile(this.templateSource);
    this.renderStyle = 'append';
  },

  render: function() {
    var that = this;
    var appended = [];
    if (this.renderStyle == 'replace') {
      this.$el.empty();
      this.renderStyle = 'append';
    }
    _.each(this.newStories, function(story) {
      var $el = that.$el.append(that.template(story.toJSON()));
      appended.push($el[0]);
    });
    if (this.$el.hasClass('tile')) {
      this.$el.masonry('reload');
    }
    this.newStories = [];
    return this;
  },

  reset: function(stories) {
    this.newStories = stories.toArray();
    this.renderStyle = 'replace';
  },

  appendStory: function(story) {
    this.newStories.push(story);
  },

  /**
   * Show stories as tiles using jQuery Masonry
   */
  tile: function() {
    var width = this.$el.width();
    this.$el.addClass('tile');
    this.$el.removeClass('list');
    this.$el.masonry({
      itemSelector: '.story',
      columnWidth: function(containerWidth) {
        var columnWidth = containerWidth;
        if (containerWidth >= 700) {
          columnWidth = containerWidth / 4;
        } 
        else if (containerWidth >= 400) {
          columnWidth = containerWidth / 2;
        }
        return columnWidth;
      }
    });
  },

  /**
   * Remove tiling created using jQuery Masonry
   */
  list: function() {
    this.$el.removeClass('tile');
    this.$el.addClass('list');
    this.$el.masonry('destroy');
  }

});
