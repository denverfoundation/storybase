/**
 * Views for the story explorer Backbone application
 */
;(function(_, Backbone, Handlebars, storybase) {
  var Explorer = storybase.explorer;
  if (_.isUndefined(Explorer.views)) {
    Explorer.views = {};
  }
  var Views = Explorer.views;

  var HandlebarsTemplateView = storybase.views.HandlebarsTemplateView;
  var Story = storybase.models.Story;
  var Stories = storybase.collections.Stories;

  // If the tooltipster jQuery plugin isn't installed, mock it so we can
  // call $(...).tooltipster(...) without error
  // TODO: This is replicated in the builder views.  We might want to do this
  // in a more global place.
  if (!$.fn.tooltipster) {
    $.fn.tooltipster = function (options) {};
  }

  Handlebars.registerPartial("story", $("#story-partial-template").html());
  Handlebars.registerPartial("story_link", $("#story-link-partial-template").html());

  Views.ExplorerApp = HandlebarsTemplateView.extend({
    el: $('#explorer'),

    options: {
      selectedFilters: {},
      bufferPx: 40,
      pixelsFromListToBottom: undefined,
      templateSource: $('#explorer-template').html(),
      // If the filter height is less than this percentage (represented as
      // a decimal), make the filters stick to the top of the window as
      // the window is scrolled.
      stickyFilterPercentage: 0.3
    },

    events: {
      "click .select-tile-view": "selectTile",
      "click .select-list-view": "selectList",
      "click #show-more": "clickShowMore",
      "change #filters select": "handleChangeFilters",
      "click #filters .clear-filters": "clearAllFilters"
    },

    initialize: function(options) {
      var that = this;
      this.selectedFilters = this.options.selectedFilters;
      // Flag to keep from re-fetching the same page of items when we're
      // scrolled near the bottom of the window, but the new items haven't yet
      // loaded
      this.isDuringAjax = false;
      // Is the tile or list view currently active
      this.activeView = null;
      // Total number of matching stories
      this.totalMatchingStories = 0;
      this.stories = new Stories();
      this.reset(this.options.storyData);
      this.messages = {
        placeNotVisible: {
          seen: false
        }
      };
      this.compileTemplates();
      this.counterView = new StoryCount({
        count: this.stories.length,
        total: this.totalMatchingStories,
        hasMore: this.hasMoreStories()
      });
      this.filterView = new Filters({
        topics: this.options.storyData.topics,
        organizations: this.options.storyData.organizations,
        places: this.options.storyData.places,
        badges: this.options.storyData.badges,
        languages: this.options.storyData.languages,
        selected: this.selectedFilters,
        stickyFilterPercentage: this.options.stickyFilterPercentage
      });
      this.storyListView = new StoryList({
        stories: this.stories
      });

      $(window).bind('scroll', function(ev) {
        that.scrollWindow(ev);
      });

      // Bind 'this' variable in callbacks to the view object
      _.bindAll(this, 'resetAll', 'showMoreStories');
    },

    getFilterNames: function() {
      return ["topics", "places", "organizations", "badges", "languages"];
    },

    setMessageSeen: function(messageName) {
      this.messages[messageName].seen = true;
    },

    resetMessageSeen: function(messageName) {
      this.messages[messageName].seen = false;
    },

    messageSeen: function(messageName) {
      return this.messages[messageName].seen;
    },

    reset: function(data) {
      this.nextUri = data.meta.next;
      this.resourceUri = data.meta.resource_uri;
      this.stories.reset(data.objects);
      this.totalMatchingStories = data.meta.total_count;
    },

    render: function() {
      var context = {};
      this.$el.html(this.template(context));
      this.counterView.render();
      this.$el.prepend(this.counterView.el);
      this.filterView.render();
      this.$el.prepend(this.filterView.el);
      this.$el.prepend('<div id="filter-proxy"></div>');
      this.filterView.setInitialProperties();
      this.$el.append(this.storyListView.el);
      this.selectView(this.options.viewType);
      this.storyListView.render();
      // Distance from story list to bottom
      // Computed as: height of the document - top offset of story list container
      // - outer height of story list container
      this.options.pixelsFromListToBottom = $(document).height() - this.storyListView.$el.offset().top - this.storyListView.$el.outerHeight();
      this.$('.select-tile-view,.select-list-view').tooltipster({
        position: 'bottom'
      });
      return this;
    },

    selectView: function(viewType) {
      if (viewType == 'list') {
        this.selectList();
      }
      else {
        this.selectTile();
      }
    },

    selectTile: function(e) {
      this.storyListView.$el.show();
      this.storyListView.tile();
      $('#view-selector li')
        .removeClass('active')
        .filter('.tile-view')
          .addClass('active');
      return false;
    },

    selectList: function(e) {
      // The Masonry plugin sets an explicit width on the container element.
      // Remove this width so the stylesheet styles take effect.
      this.storyListView.$el.css('width', '');
      this.storyListView.$el.show();
      this.storyListView.list();
      $('#view-selector li')
        .removeClass('active')
        .filter('.list-view')
          .addClass('active');
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

    /**
     * Event handler for clicking the "show more" link.
     */
    clickShowMore: function(e) {
      e.preventDefault();
      this.counterView.render({loading: true});
      this.getMoreStories(this.showMoreStories);
    },

    hasMoreStories: function() {
      return Boolean(this.nextUri);
    },

    /**
     * Retrieve more stories from the server via AJAX
     *
     * This is called both when the user scrolls to the bottom of the page
     * and when the user explicitly clicks a "Show More" link.
     *
     * @param {function} callback Callback function that is executed after
     *   stories have been successfully fetched from the server.
     *
     */
    getMoreStories: function(callback) {
        var that = this;
        if (this.hasMoreStories()) {
          this.isDuringAjax = true;
          this.storyListView.showLoading();
          $.getJSON(this.nextUri, function(data) {
            that.nextUri = data.meta.next;
            _.each(data.objects, function(storyJSON) {
              var story = new Story(storyJSON);
              that.stories.push(story);
              that.storyListView.appendStory(story);
            });
            that.isDuringAjax = false;
            that.storyListView.hideLoading();
            callback();
          });
        }
        else {
          //console.debug('No more stories');
        }
    },

    showMoreStories: function() {
      this.counterView.reset(this.stories.length, this.totalMatchingStories,
                             this.hasMoreStories());
      this.counterView.render();
      this.storyListView.render();
    },

    scrollWindow: function(e) {
      if (this._nearbottom() && !this.isDuringAjax) {
        this.getMoreStories(this.showMoreStories);
      }
    },

    getFilterQueryString: function() {
      var filterStrings = [];
      // Update the querystring based on the pull-down filters
      _.each(this.selectedFilters, function(value, key, list) {
        if (!!value && value.length > 0) {
          var values = [];
          _.each(value, function(element, index, list) {
            if (element !== "") {
              values.push(element);
            }
          });
          if (values.length > 0) {
            filterStrings.push(key + "=" + values.join(","));
          }
        }
      });
      return filterStrings.length > 0 ? '?' + filterStrings.join('&') : '';
    },

    /**
     * Get the resource URI including a query string based on the filters
     */
    getFilterUri: function() {
      var filterUri = this.resourceUri;
      var queryString = this.getFilterQueryString.call(this);
      // Push the query string to the browser history and update the url
      // to preserve the selected filters on browser's back and forward
      window.history.replaceState({queryString: queryString}, '', queryString);
      filterUri += queryString;
      return filterUri;
    },

    setFilter : function(name, value) {
      if (name == "places") {
        this.resetMessageSeen('placeNotVisible');
      }

      if (typeof value === "string") {
        this.selectedFilters[name] = [value];
      }
      else {
        this.selectedFilters[name] = value;
      }
    },

    /**
     * Reset the data and redraw all child views.
     *
     * Arguments:
     * data - response Object returned by endpoint
     */
    resetAll: function(data) {
      this.reset(data);
      this.counterView.reset(this.stories.length, this.totalMatchingStories,
                             this.hasMoreStories());
      this.counterView.render();
      this.storyListView.reset(this.stories);
      this.storyListView.render();
      this.filterView.reset({
        topics: data.topics,
        organizations: data.organizations,
        places: data.places,
        badges: data.badges,
        languages: data.languages,
        selected: this.selectedFilters
      });
      this.filterView.render();
    },

    fetchStories: function() {
      this.storyListView.spin();
      $.getJSON(this.getFilterUri(), this.resetAll);
    },

    changeFilter: function(name, value, fetch) {
      fetch = typeof fetch === "undefined" ? true : fetch;
      this.setFilter(name, value);
      if (fetch) {
        this.fetchStories();
      }
    },

    clearFilter: function(name, fetch) {
      fetch = typeof fetch === "undefined" ? true : fetch;
      this.changeFilter(name, null, fetch);
    },

    clearAllFilters: function(ev) {
      var that = this;
      ev.preventDefault();
      _.each(this.getFilterNames(), function(name) {
        that.clearFilter(name, false);
      });
      // Remove the query string from the url and replace the history state
      window.history.replaceState({queryString: ''}, '', '.');
      this.fetchStories();
    },

    handleChangeFilters: function(ev) {
      var name = ev.currentTarget.name;
      var value =  $(ev.currentTarget).val();
      this.changeFilter(name, value);
    }
  });

  var StoryCount = Views.StoryCount = HandlebarsTemplateView.extend({
    tagName: 'div',

    id: 'story-count',

    options: {
      templateSource: $('#story-count-template').html()
    },

    initialize: function() {
      this.count = this.options.count;
      this.hasMore = this.options.hasMore;
      this.total = this.options.total;
      this.compileTemplates();
    },

    render: function(options) {
      options = typeof options === "undefined" ? {} : options;
      var defaults = {
        loading: false
      };
      _.defaults(options, defaults);
      var context = {
        count: this.count,
        total: this.total,
        showMore: this.hasMore && !options.loading
      };
      this.$el.html(this.template(context));
      if (options.loading) {
        var spinner = new Spinner({
          length: this.$el.innerHeight() / 4,
          radius: this.$el.innerHeight() / 8,
          width: 2
        }).spin();
        this.$el.append(spinner.el);
      }
      return this;
    },

    reset: function(count, total, hasMore) {
      this.count = count;
      this.total = total;
      this.hasMore = hasMore;
    }

  });

  var Filters = Views.Filters = HandlebarsTemplateView.extend({
    tagName: 'div',

    id: 'filters',
    className: 'filters',

    options: {
      templateSource: $('#filters-template').html()
    },

    events: {
      // Hide fancy tooltips when filter dropdown is opened, otherwise
      // the tooltips will obscure the dropdown items
      'open select': 'removeTooltips'
    },

    initialize: function() {
      var view = this;
      this.initialOffset = null;
      this.compileTemplates();

      // Manually bind window events
      $(window).bind('scroll', function(ev) {
        view.scrollWindow(ev);
      });

      $(window).bind('resize', function(ev) {
        view.resizeWindow(ev);
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
        places: this.options.places,
        badges: this.options.badges,
        languages: this.options.languages
      };
      if (typeof this.options.selected !== "undefined") {
        _.each(this.options.selected, function(selected, filter, list) {
          _.each(selected, function(element, index, list) {
            var option = _.find(context[filter], function(obj) {
              return obj.id == element;
            });

            if (typeof option !== "undefined") {
              option.selected = true;
            }
          });
        });
      }

      return context;
    },

    /**
     * Initialize fancy tooltips to the filter selection widgets.
     *
     * @param {Object} options - Options passed to the tooltipster jQuery
     *     plugin
     */
    addTooltips: function(options) {
      this.$('select').each(function() {
        var select2 = $(this).data('select2');
        var title = $(this).attr('title');
        var tooltipOptions;
        if (title) {
          select2.container.attr('title', title);
          tooltipOptions = _.extend({
            overrideText: title,
            position: 'bottom'
          }, options);
          select2.container.tooltipster(tooltipOptions);
        }
      });
    },

    /**
     * Remove open fancy tooltips
     *
     * Code is based on the the animateOut function in the Tooltipster
     * jQuery plugin. It has to be replicated here because that plugin has
     * no public API for closing tooltips.
     */
    removeTooltips: function() {
      var tooltipTheme = '.tooltip-message';
      var $tooltipToKill = $(tooltipTheme).not('.tooltip-kill');
      var speed = 100;
      if ($tooltipToKill.length == 1) {
        $tooltipToKill.slideUp(speed, function() {
          $tooltipToKill.remove();
          $("body").css("overflow-x", "auto");
        });
        $(tooltipTheme).not('.tooltip-kill').addClass('tooltip-kill');
      }
    },

    updatePercentageHeight: function() {
      this._percentageHeight = this.$el.outerHeight() / $(window).height();
    },

    getPercentageHeight: function() {
      if (!this._percentageHeight) {
        this.updatePercentageHeight();
      }

      return this._percentageHeight;
    },

    render: function() {
      var context = this.buildContext();
      this.$el.html(this.template(context));
      var selects = this.$('select').select2({
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

      // Enable tooltips if the filters aren't stacked on a small screen.
      // We need to do this here rather than in render() because when render()
      // is called, the view's element hasn't yet been added to the DOM, so
      // we can't check its height.
      this.updatePercentageHeight();
      if (this.getPercentageHeight() < this.options.stickyFilterPercentage) {
        this.addTooltips();
      }
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

      this.updatePercentageHeight();

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

      if (scrollTop > this.initialOffset.top &&
          this.getPercentageHeight() < this.options.stickyFilterPercentage) {
        $('#filter-proxy').addClass('shown').height(this.$el.outerHeight() + 'px');
        this.$el.addClass('sticky');
        this.$el.width(this.initialWidth);
      }
      else {
        $('#filter-proxy').removeClass('shown');
        this.$el.removeClass('sticky');
      }
    }
  });

  var StoryList = Views.StoryList = HandlebarsTemplateView.extend({
    tagName: 'ul',

    id: 'story-list',

    options: {
      templateSource: $('#story-template').html()
    },

    initialize: function() {
      this.newStories = this.options.stories.toArray();
      this.compileTemplates();
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

    /**
     * Display a spinner while data is loading
     */
    spin: function() {
      var height = 200;
      this.$el.empty();
      this.$el.width('100%');
      this.$el.css('min-height', height);
      var spinner = new Spinner({
        top: height / 2,
        left: this.$el.width() / 2
      }).spin(this.$el[0]);
    },

    /**
     * Display a loading more message while data is loading
     */
    showLoading: function() {
      if (_.isUndefined(this.$loadingEl)) {
        this.$loadingEl = $('<div>').attr('id', 'loading')
                                    .html('<span class="text">'+gettext("Loading more stories")+"</span>")
                                    .insertAfter(this.$el);
        if (window.Spinner) {
          this.$loadingEl.append(new Spinner({
            length: this.$loadingEl.innerHeight() / 10,
            radius: this.$loadingEl.innerHeight() / 12,
            width: 4
          }).spin().el);
        }
      }
      else {
        this.$loadingEl.insertAfter(this.$el);
      }

      return this;
    },

    /**
     * Hide the loading message.
     */
    hideLoading: function() {
      if (this.$loadingEl) {
        this.$loadingEl.remove();
      }
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
      this.$el.find('li').removeClass('container_12');
      this.$el.masonry({
        itemSelector: '.story',
        // Base the column width on the elements.  It looks like newer
        // versions of the Guiders library support this by specifying
        // a selector for the columnWidth option.
        // See http://masonry.desandro.com/options.html#columnwidth
        columnWidth: this.$('.story').outerWidth(),
        // Assign an explicit width to the container so it can be horizontally
        // centered with CSS
        isFitWidth: true
      });
    },

    /**
     * Remove tiling created using jQuery Masonry
     */
    list: function() {
      this.$el.removeClass('tile');
      this.$el.addClass('list');
      this.$el.find('li').addClass('container_12');
      this.$el.masonry('destroy');
    }

  });
})(_, Backbone, Handlebars, storybase);
