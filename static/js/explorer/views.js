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
    this.nextUrl = this.options.storyData.next;
    this.stories = new storybase.collections.Stories;
    this.stories.reset(this.options.storyData.objects);
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

  /*
  getMoreStories: function() {
      var that = this;
      if (this.nextUrl) {
        $.getJSON(this.nextUrl, function(data) {
          this.nextUrl = data.meta.next;
          _.each(data.objects, function(storyJSON) {
            var story = new storybase.models.Story(storyJSON);
            that.stories.push(story);
            that.storyListView.appendStory(story);
          });
        });
      }
      console.debug('No more stories');
  },
  */

  getMoreStories: function() {
    if (typeof this.storycount === "undefined") {
      this.storycount = 0;
    }
    for (var i = 0; i <= 5; i++) {
      this.storycount++;
      var story = new storybase.models.Story({
          byline: "Test Author",
          contact_info: "",
          created: "2012-04-11T14:50:00",
          languages: [{id: "en", name: "English"}],
          last_edited: "2012-04-11T14:50:00",
          on_homepage: false,
          organizations: [],
          projects: [],
          summary: "synergize SEO gotta grok it before you rock it curation discuss vast wasteland Gutenberg, gamification Gutenberg parenthesis pay curtain serendipity Frontline Encyclo, experiment get me rewrite paywall future of context horse-race coverage. WaPo aggregation newspaper strike MinnPost try PR Voice of San Diego Walter Cronkite died for your sins dying content is king column-inch the power of the press belongs to the person who owns one circulation data journalism, SEO gutter TechCrunch we need a Nate Silver copyright a giant stack of newspapers that you'll never read discuss dingbat Google News Jay Rosen Alberto Ibarguen.", 
          title: "Test Story " + this.storycount,
          url: "/stories/test-story-" + i
      });
      this.stories.push(story);
      this.storyListView.appendStory(story);
    }
  },

  scrollWindow: function(e) {
    if (this._nearbottom()) {
      this.getMoreStories();
      this.storyListView.render();
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

  templateSource: $('#story-template').html(),

  initialize: function() {
    this.newStories = this.options.stories.toArray();
    this.template = Handlebars.compile(this.templateSource);
  },

  render: function() {
    var that = this;
    var appended = [];
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
