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
      console.debug(this.cluster_);
      this.stories_ = _.uniq(_.map(this.cluster_.getMarkers(), 
        function(marker) {
          console.debug(marker);
          return marker.marker.story;
      }));
      console.debug(this.stories_.length);
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
    "change #filters select": "changeFilters"
  },

  initialize: function() {
    var that = this;
    _.defaults(this.options, this.defaults);
    this.selectedFilters = this.options.selectedFilters;
    // Point around which to filter stories 
    this.near = null;
    // Radius in miles around this.near to filter stories
    this.distance = storybase.explorer.globals.SEARCH_DISTANCE;
    // Flag to keep from re-fetching the same page of items when we're 
    // scrolled near the bottom of the window, but the new items haven't yet
    // loaded
    this.isDuringAjax = false; 
    this.stories = new storybase.collections.Stories;
    this.reset(this.options.storyData);
    this.template = Handlebars.compile(this.templateSource);
    this.counterView = new storybase.explorer.views.StoryCount({
      count: this.stories.length
    });
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
      stories: this.stories,
      parentView: this
    });

    $(window).bind('scroll', function(ev) {
      that.scrollWindow(ev);
    });

    // Bind 'this' variable in callbacks to the view object
    _.bindAll(this, ['resetAll']);
  },

  reset: function(data) {
    this.nextUri = data.meta.next;
    this.resourceUri = data.meta.resource_uri;
    this.stories.reset(data.objects);
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
      this.counterView.setCount(this.stories.length);
      this.counterView.render();
      this.storyListView.render();
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

  setNear: function(point) {
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
    this.counterView.setCount(this.stories.length);
    this.counterView.render();
    this.storyListView.reset(this.stories);
    this.storyListView.render();
    this.mapView.reset(this.stories);
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
    $.getJSON(this.getFilterUri(), this.resetAll);
  },

  changeFilters: function(ev) {
    var that = this;
    var name = ev.currentTarget.name;
    var value =  $(ev.currentTarget).val();
    this.setFilter(name, value);
    this.fetchStories();
  }
});

storybase.explorer.views.StoryCount = Backbone.View.extend({
  tagName: 'h3',

  id: 'story-count',

  templateSource: $('#story-count-template').html(),

  initialize: function() {
    this.count = this.options.count;
    this.template = Handlebars.compile(this.templateSource);
  },

  render: function() {
    var context = {
      count: this.count
    };
    this.$el.html(this.template(context));
    return this;
  },

  setCount: function(count) {
    this.count = count;
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
    this.markerTemplate = Handlebars.compile($("#story-marker-template").html()); 
    this.searchTemplate = Handlebars.compile($('#proximity-search-template').html());
    this.initialCenter = new L.LatLng(storybase.explorer.globals.MAP_CENTER[0],
                                      storybase.explorer.globals.MAP_CENTER[1]);
    this.initialZoom = storybase.explorer.globals.MAP_ZOOM_LEVEL;

    // Bind our callbacks to the view object
    _.bindAll(this, ['redrawMap']);
    this.$el.append('<div id="' + this.mapId + '"></div>');
    this.map = null;
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
    }
    else {
      // Map has already been initialized
      this.clusterer.clearMarkers();
    }

    var placeMarker = function(bundle) {
        var latlng = new L.LatLng(bundle.point[0], bundle.point[1]);
        var marker = new StoryMarker(latlng, bundle.story);
        that.clusterer.addMarker(marker);
        var popupContent = that.markerTemplate(bundle.story.toJSON());
        marker.bindPopup(popupContent);
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

    this.stories.each(placeStoryMarkers); 
  },

  reset: function(stories) {
    this.stories = stories;
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
  geocode: function(address, callback) {
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
          callback({
            'lat': data[0].lat,
            'lng': data[0].lon
          });
        }
        // TODO: Do something on geocoding failure
      }
    });
    
  },

  /**
   * Post geocoding callback
   */
  redrawMap: function(point) {
    // Recenter the map based on the geocoded point 
    var center = new L.LatLng(point.lat, point.lng);
    this.map.setView(center, this.map.getZoom());
    this.parentView.setNear(point);
    this.parentView.fetchStories();
  },

  proximitySearch: function() {
    var address = this.$('#' + this.searchFieldId).val();
    this.geocode(address, this.redrawMap);
  },

  clearProximitySearch: function() {
    this.$('#' + this.searchFieldId).val('');
    this.parentView.setNear(null).fetchStories();
    this.map.setView(this.initialCenter, this.initialZoom);
  }
});
