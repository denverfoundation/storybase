/**
 * Views for the story explorer Backbone application
 */
Namespace('storybase.explorer');

Handlebars.registerPartial("story", $("#story-partial-template").html());

Handlebars.registerPartial("story_link", $("#story-link-partial-template").html());

StoryMarker = L.Marker.extend({
  initialize: function (latlng, story, options) {
    L.Util.setOptions(this, options);
    this._latlng = latlng;
    this.story = story;
  }
});

StoryClusterMarker = ClusterMarker_.extend({
  /**
   * Override the original to pass the cluster object to be able to have
   * access to the markers and stories
   */
  initialize: function(latLng_, cluster_, count_, styles_, padding_) {
    this.reset({latLng:latLng_, cluster: cluster_, count: count_, styles: styles_, padding: padding_});
  },

  /**
   * Override the original to display the marker count based on the number
   * of stories, not the number of markers.  I'm still not sure this is
   * a good idea.
   */
  reset: function(opts) {
    if (!opts || typeof opts !== "object")
      return;

    var updated = 0;
    if (typeof opts.latLng === "object" && opts.latLng != this.latlng_) {
      this.latlng_ = opts.latLng;
      updated = 1;
    }
    if (typeof opts.cluster === "object" && opts.cluster != this.cluster_) {
      this.cluster_ = opts.cluster;
      this.stories_ = _.uniq(_.map(this.cluster_.getMarkers(), 
        function(marker) {
          return marker.marker.story;
      }));
      this.count_ = this.stories_.length; 
    }

    var styles_updated = 0;
    if (typeof opts.styles === "object" && opts.styles != this.styles_) {
      this.styles_ = opts.styles;
      updated = 1;
      styles_updated = 1;
    }

    if (this.count_) {
      var index = 0;
      var dv = this.count_;
      while (dv !== 0) {
          dv = parseInt(dv / 10, 10);
          index ++;
      }

      var styles = this.styles_;

      if (styles.length < index) {
          index = styles.length;
      }
      this.url_ = styles[index - 1].url;
      this.height_ = styles[index - 1].height;
      this.width_ = styles[index - 1].width;
      this.textColor_ = styles[index - 1].opt_textColor;
      this.anchor_ = styles[index - 1].opt_anchor;
      this.index_ = index;
      updated = 1;
    }

    if (typeof opts.padding === "number" && this.padding_ != opts.padding) {
      this.padding_ = opts.padding;
      updated = 1;
    }

    this.updated |= updated;
  },

  onClick_: function(cluster) {
    var map = cluster.map_;
    var popup = new L.Popup();
    var storiesJSON = _.map(this.stories_, function(story) {
      return story.toJSON();
    });
    var popupContent = StoryClusterMarker.template({
      stories: storiesJSON
    });
    popup.setLatLng(cluster.latlng_);
    popup.setContent(popupContent);
    map.openPopup(popup); 
  }
});
StoryClusterMarker.template = Handlebars.compile($('#story-list-marker-template').html());
// Monkey patch leafclusterer's ClusterMarker_ to use our inherited 
// class
ClusterMarker_ = StoryClusterMarker;

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
    "click #show-more": "clickShowMore",
    "change #filters select": "handleChangeFilters",
    "click #filters .clear-filters": "clearAllFilters",
  },

  initialize: function() {
    var that = this;
    _.defaults(this.options, this.defaults);
    this.selectedFilters = this.options.selectedFilters;
    // Point around which to filter stories 
    this.near = null;
    // Radius in miles around this.near to filter stories
    this.distance = storybase.explorer.globals.SEARCH_DISTANCE;
    // Should only stories with geographic points be shown
    this.onlyPoints = false;
    // Flag to keep from re-fetching the same page of items when we're 
    // scrolled near the bottom of the window, but the new items haven't yet
    // loaded
    this.isDuringAjax = false; 
    // Is the tile, list or map view currently active
    this.activeView = null;
    // Total number of matching stories
    this.totalMatchingStories = 0;
    this.stories = new storybase.collections.Stories;
    this.reset(this.options.storyData);
    this.messages = {
      placeNotVisible: {
        seen: false
      }
    };
    this.template = Handlebars.compile(this.templateSource);
    this.counterView = new storybase.explorer.views.StoryCount({
      count: this.stories.length,
      total: this.totalMatchingStories,
      hasMore: this.hasMoreStories()
    });
    this.filterView = new storybase.explorer.views.Filters({
      topics: this.options.storyData.topics,
      organizations: this.options.storyData.organizations,
      places: this.options.storyData.places,
      projects: this.options.storyData.projects,
      languages: this.options.storyData.languages,
      selected: this.selectedFilters
    });
    this.storyListView = new storybase.explorer.views.StoryList({
      stories: this.stories
    });
    this.mapView = new storybase.explorer.views.Map({
      stories: this.stories,
      boundaryPoints: this.options.storyData.boundaries,
      parentView: this
    });

    $(window).bind('scroll', function(ev) {
      that.scrollWindow(ev);
    });

    // Bind 'this' variable in callbacks to the view object
    _.bindAll(this, 'resetAll', 'showMoreStories');
  },

  getFilterNames: function() {
    return ["topics", "places", "organizations", "projects", "languages"];
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
    var refetchStories = false;
    this.activeView = 'tile';
    if (this.hasNear()) {
      // Proximity search was enabled
      // Disable it
      this.setNear(null);
      refetchStories = true;
    }
    if (this.onlyPoints) {
      this.onlyPoints = false;
      refetchStories = true;
    }
    if (refetchStories) {
      this.fetchStories();
    }
    this.mapView.$el.hide();
    this.storyListView.$el.show();
    this.storyListView.tile();
    $('#view-selector li')
      .removeClass('active')
      .filter('.tile-view')
        .addClass('active');
    return false;
  },

  selectList: function(e) {
    var refetchStories = false;
    this.activeView = 'list';
    if (this.hasNear()) {
      // Proximity search was enabled
      // Disable it
      this.setNear(null);
      refetchStories = true;
    }
    if (this.onlyPoints) {
      this.onlyPoints = false;
      refetchStories = true;
    }
    if (refetchStories) {
      this.fetchStories();
    }
    this.mapView.$el.hide();
    this.storyListView.$el.show();
    this.storyListView.list();
    $('#view-selector li')
      .removeClass('active')
      .filter('.list-view')
        .addClass('active');
    return false;
  },

  selectMap: function(e) {
    this.activeView = 'map';
    if (!this.onlyPoints) {
      this.onlyPoints = true;
      this.fetchStories();
    }
    this.storyListView.$el.hide();
    this.mapView.$el.show();
    $('#view-selector li')
      .removeClass('active')
      .filter('.map-view')
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

  getMoreStories: function(callback) {
      var that = this;
      if (this.hasMoreStories()) {
        this.isDuringAjax = true;
        $.getJSON(this.nextUri, function(data) {
          that.nextUri = data.meta.next;
          _.each(data.objects, function(storyJSON) {
            var story = new storybase.models.Story(storyJSON);
            that.stories.push(story);
            that.storyListView.appendStory(story);
            that.mapView.appendStory(story);
          });
          that.isDuringAjax = false;
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
    if (this._nearbottom() && !this.isDuringAjax && this.activeView != 'map') {
      this.getMoreStories(this.showMoreStories);
    }
  },

  /**
   * Get the resource URI including a query string based on the filters
   */
  getFilterUri: function() {
    var filterUri = this.resourceUri;
    var filterStrings = [];
    // Update the querystring based on the pull-down filters
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
    // Update the querystring based on the address search
    if (this.near !== null) {
      filterStrings.push("near=" + this.near.lat + '@' + this.near.lng + ',' + this.distance);
    }
    // Update the querystring based on if we only want to show stories with
    // places
    if (this.onlyPoints) {
      filterStrings.push("num_points__gt=0");
    }
    filterUri = filterStrings.length > 0 ? filterUri + '?' : filterUri;
    filterUri += filterStrings.join("&");
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

  // Is proximity search enabled?
  hasNear: function() {
    return this.near !== null;
  },

  setNear: function(point) {
    if (point === null) {
      console.debug("clearing proximity search");
    }
    this.near = point
    return this;
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
    this.mapView.reset(this.stories, data.boundaries);
    this.mapView.render();
    this.filterView.reset({
      topics: data.topics,
      organizations: data.organizations,
      places: data.places,
      projects: data.projects,
      languages: data.languages,
      selected: this.selectedFilters
    });
    this.filterView.render();
  },

  fetchStories: function() {
    if (this.activeView !== 'map') {
      this.storyListView.spin();
    }
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
    this.fetchStories();
  },

  handleChangeFilters: function(ev) {
    var name = ev.currentTarget.name;
    var value =  $(ev.currentTarget).val();
    this.changeFilter(name, value);
  }
});

storybase.explorer.views.StoryCount = Backbone.View.extend({
  tagName: 'div',

  id: 'story-count',

  templateSource: $('#story-count-template').html(),

  initialize: function() {
    this.count = this.options.count;
    this.hasMore = this.options.hasMore;
    this.total = this.options.total;
    this.template = Handlebars.compile(this.templateSource);
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

storybase.explorer.views.Filters = Backbone.View.extend({
  tagName: 'div',

  id: 'filters',
  className: 'filters',

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
  
  id: 'map-container',  

  mapId: 'map',

  searchFieldId: 'proximity-search-address',

  searchButtonId: 'do-proximity-search',

  clearButtonId: 'clear-proximity-search',

  events: function() {
    var events = {};
    events["click #" + this.searchButtonId] = "proximitySearch"; 
    events["click #" + this.clearButtonId] = "clearProximitySearch";
    return events;
  },

  initialize: function() {
    this.parentView = this.options.parentView;
    this.stories = this.options.stories;
    this.boundaryPoints = this.options.boundaryPoints;
    this.boundaryLayers = new L.FeatureGroup(); 
    this.markerTemplate = Handlebars.compile($("#story-marker-template").html()); 
    this.searchTemplate = Handlebars.compile($('#proximity-search-template').html());
    this.mapMovePopupTemplate = Handlebars.compile($('#map-move-popup-template').html());
    this.initialCenter = new L.LatLng(storybase.explorer.globals.MAP_CENTER[0],
                                      storybase.explorer.globals.MAP_CENTER[1]);
    this.initialZoom = storybase.explorer.globals.MAP_ZOOM_LEVEL;

    // Bind our callbacks to the view object
    _.bindAll(this, 'redrawMap', 'geocode', 'geocodeFail', 
              'checkPlaceInMapBounds', 'clearPlaceFilters', 'keepPlaceFilters', 
              '_placeMarker', '_placeStoryMarkers');
    this.$el.append('<div id="' + this.mapId + '"></div>');
    this.map = null;
  },

  /**
   * Convert a 2-dimensional array of latitude/longitude pairs to
   * an array of L.LatLng objects
   */
  makeLatLngs: function(featurePoints) {
    return _.map(featurePoints, function(point) {
      var latlng = new L.LatLng(point[1], point[0]);
      return latlng; 
    });
  },

  /**
   * Create a mapping library objects representing place boundaries  
   * @param {array} boundaryPoints Three dimensional array representing
   *    multipolygons.  The top level of the array represents the
   *    different place boundaries, the next level is each shape in the
   *    boundary, and the smallest level is a latitude/longitude pair.
   * @return {array} An array of L.MultiPolygon objects 
   */
  makeBoundaries: function(boundaryPoints) {
    var that = this;
    var boundaries = [];
    _.each(boundaryPoints, function(singleBoundaryPoints) {
      var singleBoundaryLatlngs = [];  
      _.each(singleBoundaryPoints, function(shapePoints) {
        var latlngs = that.makeLatLngs(shapePoints);
        singleBoundaryLatlngs.push(latlngs);
      });
      var mp = new L.MultiPolygon(singleBoundaryLatlngs);
      boundaries.push(mp);
    });
    return boundaries;
  },

  keepPlaceFilters: function(popup) {
    this.parentView.setMessageSeen('placeNotVisible');
    this.map.removeLayer(popup);
  },

  clearPlaceFilters: function(popup) {
    this.parentView.clearFilter('places');
    this.map.removeLayer(popup);
  },

  /**
   * Check that selected places are visible on the map.
   * This is an event handler that should be bound to the map's 'move'
   * event.
   */
  checkPlaceInMapBounds: function() {
    var that = this;
    if (this.boundaryPoints.length) {
      // One or more places have been selected
      var boundaryBounds = this.boundaryLayers.getBounds();
      var mapBounds = this.map.getBounds();
      if (!mapBounds.intersects(boundaryBounds) &&
          !this.parentView.messageSeen('placeNotVisible')) {
        var popupContent = this.mapMovePopupTemplate({}); 
        var popup = new L.Popup();
        popup.setLatLng(this.map.getCenter());
        popup.setContent(popupContent);
        this.map.openPopup(popup);
        $('#keep-place-filters').click(function(e) {
          that.keepPlaceFilters(popup);
        });
        $('#clear-place-filters').click(function(e) {
          that.clearPlaceFilters(popup);
        });
      }
    }
  },

  /**
   * Return a list of points and their associated stories
   * @param {story} story Story model instance
   * @param {array} points An array of arrays with each inner array
   *    representing a point. array[0] is longitude, array[1] is latitude
   * @return {array} An array of objects with each object having a story
   *    story attribute set to the story parameter and a point array set
   *    to one of the elements in points
   */
  _makeBundle: function(story, points) {
    return _.map(points, function(point) {
      return {
        story: story,
        point: point
      };
    });
  },

  /**
   * Place a marker on the map
   * @param {object} bundle An object with a story and point attribute, as
   *     returned by _makeBundle()
   */
  _placeMarker: function(bundle) {
    var latlng = new L.LatLng(bundle.point[0], bundle.point[1]);
    var marker = new StoryMarker(latlng, bundle.story);
    this.clusterer.addMarker(marker);
    var popupContent = this.markerTemplate(bundle.story.toJSON());
    marker.bindPopup(popupContent);
  },

  /**
   * Place markers on the map for each point associated with a story
   * @param {object} story a Story model instance
   */
  _placeStoryMarkers: function(story) {
    _.each(this._makeBundle(story, story.get("points")), this._placeMarker); 
  },

  render: function() {
    var that = this;
    if (this.map === null) {
      // Map has not yet been initialized
      this.$('#' + this.mapId).width(this.$el.parent().width());
      this.$('#' + this.mapId).height(425);
      this.map = new L.Map(this.mapId, {
        // Setting the closePopupOnClick option to false is neccessary
        // to make our cluster popup work.
        closePopupOnClick: false
      });
      this.map.setView(this.initialCenter, this.initialZoom);
      
      // See http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames 
      var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
          osmAttrib = 'Map data &copy; 2012 OpenStreetMap contributors',
          osm = new L.TileLayer(osmUrl, {maxZoom: 18, attribution: osmAttrib});
      this.map.addLayer(osm);
      // Initialize the clusterer
      var clustererOpts = {
        maxZoom: 30,
        gridSize: 30 
      };
      this.clusterer = new LeafClusterer(this.map, null, clustererOpts);
      this.$el.append(this.searchTemplate({
        button_id: this.searchButtonId,
        field_id: this.searchFieldId,
        clear_button_id: this.clearButtonId
      }));
      this.map.addLayer(this.boundaryLayers);
      this.map.on('move', this.checkPlaceInMapBounds);
      
    }
    else {
      // Map has already been initialized
      this.clusterer.clearMarkers();
    }

    this.stories.each(that._placeStoryMarkers); 

    // Remove existing boundaries from the map
    this.boundaryLayers.clearLayers();
    // Add new boundaries
    if (this.boundaryPoints.length) {
      var polygons = this.makeBoundaries(this.boundaryPoints);
      _.each(polygons, function(polygon) {
        that.boundaryLayers.addLayer(polygon);
      });
      // Zoom and recenter the map to the selected boundaries
      var boundaryBounds = this.boundaryLayers.getBounds();
      this.map.fitBounds(boundaryBounds);
    }
  },

  reset: function(stories, boundaryPoints) {
    this.stories = stories;
    this.boundaryPoints = boundaryPoints;
  },

  /**
   * Wrapper for geocoding method
   *
   * The heavy lifting is handled by a service-specific method
   */
  geocode: function(address, success, failure) {
    this.geocodeLocal(address, success, failure);
  },

  /**
   * Geocode an address using Nominatim
   *
   * Nominatim is OpenStreetMap's geocoding service.
   * See http://http://nominatim.openstreetmap.org/
   *
   * This view could be extended and this method overriden to
   * use a different Geocoding Service.
   *
   */
  geocodeNominatim: function(address, success, failure) {
    $.ajax('http://nominatim.openstreetmap.org/search/', {
      dataType: 'jsonp',
      data: {
        format: 'json',
        q: address,
      },
      jsonp: 'json_callback',
      success: function(data, textStatus, jqXHR) {
        if (data.length) {
          // Found a point for the address
          success({
            'lat': data[0].lat,
            'lng': data[0].lon
          });
        }
        else {
          failure(address);
        }
      }
    });
    
  },

  /**
   * Geocode using the local geocoding proxy
   */
  geocodeLocal: function(address, success, failure) {
    // TODO: Don't hardcode this URL
    $.ajax('/api/0.1/geocode', {
      dataType: 'json',
      data: {
        q: address,
      },
      success: function(data, textStatus, jqXHR) {
        if (data.meta.total_count > 0) {
          // Found a point for the address
          success({
            'lat': data.objects[0].lat,
            'lng': data.objects[0].lng
          });
        }
        else {
          failure(address);
        }
      }
    });
  },

  /**
   * Post-geocoding callback when geocoding succeeds
   */
  redrawMap: function(point) {
    this.parentView.setMessageSeen('placeNotVisible');
    // Recenter the map based on the geocoded point 
    console.debug("Found point (" + point.lat + "," + point.lng + ")")
    var center = new L.LatLng(point.lat, point.lng);
    this.map.setView(center, storybase.explorer.globals.MAP_POINT_ZOOM_LEVEL);
    this.parentView.setNear(point);
    this.parentView.fetchStories();
  },

  geocodeFail: function(address) {
    // TODO: Do something more exciting when geocoding fails
    console.debug("Geocoding of address " + address + " failed");
    var popupContent = "<p>Geocoding of address " + address + " failed.  Try including a city and state in your address.</p>"; 
    var popup = new L.Popup();
    popup.setLatLng(this.map.getCenter());
    popup.setContent(popupContent);
    this.map.openPopup(popup);
  },

  proximitySearch: function() {
    var address = this.$('#' + this.searchFieldId).val();
    this.geocode(address, this.redrawMap, this.geocodeFail);
  },

  clearProximitySearch: function() {
    this.$('#' + this.searchFieldId).val('');
    this.parentView.setNear(null).fetchStories();
    this.map.setView(this.initialCenter, this.initialZoom);
  },

  appendStory: function(story) {
    this.stories.push(story);
    this._placeStoryMarkers(story);
  }
});
