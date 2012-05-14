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
    "click .select-list-view": "selectList"
  },

  initialize: function() {
    var that = this;
    _.defaults(this.options, this.defaults);
    console.debug(this.options.storyData);
    this.nextUrl = this.options.storyData.next;
    this.stories = new storybase.collections.Stories;
    this.stories.reset(this.options.storyData.objects);
    //console.debug(this.stories.toJSON());
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

  render: function() {
    var opts = this.options;
    var context = {
    };
    this.$el.html(this.template(context));
    this.filterView.render();
    this.$el.prepend(this.filterView.el);
    this.filterView.setInitialProperties();
    this.storyListView.render();
    this.$el.append(this.storyListView.el);
    // Distance from story list to bottom
    // Computed as: height of the document - top offset of story list container
    // - outer height of story list container
    this.options.pixelsFromListToBottom = $(document).height() - this.storyListView.$el.offset().top - this.storyListView.$el.outerHeight(); 
    this.selectTile();
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
    console.debug(pixelsFromWindowBottomToBottom);
    return (pixelsFromWindowBottomToBottom - opts.bufferPx < opts.pixelsFromListToBottom);
  },

  getMoreStories: function() {
      var that = this;
      if (this.nextUrl) {
        $.getJSON(this.nextUrl, function(data) {
          this.nextUrl = data.meta.next;
          _.each(data.objects, function(storyJSON) {
            that.stories.push(new storybase.models.Story(storyJSON));
          });
        });
      }
      console.debug('No more stories');
  },

  scrollWindow: function(e) {
    if (this._nearbottom()) {
      this.getMoreStories();
    }
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

  render: function() {
    var context = {
      topics: this.options.topics,
      organizations: this.options.organizations,
      projects: this.options.projects,
      languages: this.options.languages,
    }
    this.$el.html(this.template(context));
    return this;
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

  templateSource: $('#story-list-template').html(),

  initialize: function() {
    this.stories = this.options.stories;
    this.template = Handlebars.compile(this.templateSource);
  },

  render: function() {
    var context = {
       stories: this.stories.toJSON()
    }
    this.$el.html(this.template(context));
    return this;
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
