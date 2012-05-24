/**
 * Views for the story explorer Backbone application
 */
Namespace('storybase.explorer');

Handlebars.registerPartial("story", $("#story-partial-template").html());

storybase.explorer.views.ExplorerApp = Backbone.View.extend({
  el: $('#explorer'),

  templateSource: $('#explorer-template').html(),

  defaults: {
    selectedFilters: {},
    bufferPx: 40,
    pixelsFromListToBottom: undefined
  },

  events: {
    "click .select-tile-view": "selectTile",
    "click .select-list-view": "selectList",
    "click .select-map-view": "selectMap",
    "change #filters select": "changeFilters"
  },

  initialize: function() {
    var that = this;
    _.defaults(this.options, this.defaults);
    this.selectedFilters = this.options.selectedFilters;
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
      places: this.options.storyData.places,
      projects: this.options.storyData.projecs,
      languages: this.options.storyData.languages,
      selected: this.selectedFilters
    });
    this.storyListView = new storybase.explorer.views.StoryList({
      stories: this.stories
    });
    this.mapView = new storybase.explorer.views.Map({
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
    this.$el.append(this.mapView.el);
    this.mapView.render();
    this.selectView(this.options.viewType);
    this.storyListView.render();
    // Distance from story list to bottom
    // Computed as: height of the document - top offset of story list container
    // - outer height of story list container
    this.options.pixelsFromListToBottom = $(document).height() - this.storyListView.$el.offset().top - this.storyListView.$el.outerHeight(); 
    return this;
  },

  selectView: function(viewType) {
    if (viewType == 'list') {
      this.selectList();
    }
    else if (viewType == 'map') {
      this.selectMap();
    }
    else {
      this.selectTile();
    }
  },

  selectTile: function(e) {
    this.mapView.$el.hide();
    this.storyListView.$el.show();
    this.storyListView.tile();
    return false;
  },

  selectList: function(e) {
    this.mapView.$el.hide();
    this.storyListView.$el.show();
    this.storyListView.list();
    return false;
  },

  selectMap: function(e) {
    this.storyListView.$el.hide();
    this.mapView.$el.show();
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
        var values = [];
        _.each(value, function(element, index, list) {
          if (element != "") {
            values.push(element);
          }
        });
        if (values.length > 0) {
          filterStrings.push(key + "=" + values.join(","));
        }
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
      that.reset(data);
      that.storyListView.reset(that.stories);
      that.storyListView.render();
      that.filterView.reset({
        topics: data.topics,
        organizations: data.organizations,
        places: data.places,
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
      places: this.options.places,
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

storybase.explorer.views.Map = Backbone.View.extend({
  tagName: 'div',
  
  id: 'map',  

  initialize: function() {
    this.stories = this.options.stories;
    this.markerTemplate = Handlebars.compile($("#story-marker-template").html()); 
  },

  render: function() {
    var that = this;
    // TODO: Set width/height more inteligently
    this.$el.width(this.$el.parent().width());
    this.$el.height(500);
    var map = new L.Map(this.id);
    var center = new L.LatLng(storybase.explorer.globals.MAP_CENTER[0],
                              storybase.explorer.globals.MAP_CENTER[1]);
    map.setView(center, 10);
    // Initialize the clusterer
    var clustererOpts = {
      maxZoom: 30,
      gridSize: 30 
    };
    var clusterer = new LeafClusterer(map, null, clustererOpts);
    
    // See http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames 
    var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        osmAttrib = 'Map data &copy; 2012 OpenStreetMap contributors',
        osm = new L.TileLayer(osmUrl, {maxZoom: 18, attribution: osmAttrib});
    var placeMarker = function(bundle) {
        var latlng = new L.LatLng(bundle.point[0], bundle.point[1]);
        var marker = new L.Marker(latlng);
        clusterer.addMarker(marker);
        var popupContent = that.markerTemplate(bundle.story.toJSON());
        marker.bindPopup(popupContent);
        //map.addLayer(marker);
    };
    var makeBundle = function(story, points) {
      return _.map(points, function(point) {
        return {
          story: story,
          point: point
        };
      });
    };
    var placeStoryMarkers = function(story) {
      _.each(makeBundle(story, story.get("points")), placeMarker); 
    };
    map.addLayer(osm);

    this.stories.each(placeStoryMarkers); 
  }
});
