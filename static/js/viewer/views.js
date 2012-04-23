/**
 * Views for the story viewer Backbone application
 */
Namespace('storybase.viewer');

// Translations for interface text
Globalize.addCultureInfo('en', {
  messages: {
    "Topic Map": "Topic Map"
  }
});

Globalize.addCultureInfo('es', {
  messages: {
    "Topic Map": "Mapa Temático"
  }
});


// Container view for the viewer application.
// It delegates rendering and events for the entire app to views
// rendering more specific "widgets"
storybase.viewer.views.ViewerApp = Backbone.View.extend({
  // Initialize the view
  initialize: function() {
    this.navigationView = new storybase.viewer.views.StoryNavigation(); 
    this.headerView = new storybase.viewer.views.StoryHeader();
    this.sections = this.options.sections;
    this.story = this.options.story;
    this.setSection(this.sections.at(0), {showActiveSection: false});
    _.bindAll(this, 'handleScroll');
    $(window).scroll(this.handleScroll);
  },

  // Add the view's container element to the DOM and render the sub-views
  render: function() {
    this.$el.addClass(this.elClass);
    this.$('footer').append(this.navigationView.el);
    this.navigationView.render();
    this.$('.summary').show();
    this.$('.section').show();
    return this;
  },

  // Update the active story section in the sub-views
  updateSubviewSections: function() {
    this.navigationView.setSection(this.activeSection);
    this.headerView.setSection(this.activeSection);
  },

  // Show the active section
  showActiveSection: function() {
    throw "showActiveSection() is not implemented";
  },

  // Set the active story section
  setSection: function(section, options) {
    options = typeof options !== 'undefined' ? options : {};
    var showActiveSection = options.hasOwnProperty('showActiveSection') ? options.showActiveSection : true;
    this.activeSection = section;
    if (showActiveSection) {
      this.showActiveSection();
    }
    this.updateSubviewSections();
  },

  // Like setSection(), but takes a section ID as an argument instead of
  // a Section model instance object
  setSectionById: function(id) {
    this.setSection(this.sections.get(id));
  },

  // Convenience method to get the element for the active
  activeSectionEl: function() {
    return this.$('#' + this.activeSection.id);
  },

  // Event handler for scroll event
  handleScroll: function(e) {
    // Do nothing. Subclasses might want to implement this to do some work
  }
});

// View for the story viewer header.
// Updates the section heading title when the active section changes
storybase.viewer.views.StoryHeader = Backbone.View.extend({
  el: 'header',

  render: function() {
    var $titleEl = this.$el.find('.section-title').first();
    if ($titleEl.length == 0) {
      $titleEl = $('<h2 class="section-title">');
      this.$el.append($titleEl);
    }
    $titleEl.text(this.section.get('title'));
    return this;
  },

  setSection: function(section) {
    this.section = section;
    this.render();
  }
});

// View to provide previous/next buttons to navigate between sections
storybase.viewer.views.StoryNavigation = Backbone.View.extend({
  tagName: 'nav',

  className: 'story-nav',

  initialize: function() {
    this.section = null;
    if (this.options.hasOwnProperty('addlLinks')) {
      this.addlLinks = this.options.addlLinks.map(function(link) {
        return {
         text: link.text,
         id: link.id,
         href: link.hasOwnProperty('href') ? link.href: '#'
       }
      });
    }
    else {
      this.addlLinks = [];
    }
  },

  render: function() {
    var context = {};
    if (this.section) {
      context.next_section = this.section.collection.get(
        this.section.get('next_section_id'));
      context.previous_section = this.section.collection.get(
        this.section.get('previous_section_id'));
    }
    context.addl_links = this.addlLinks;

    this.$el.html(ich.navigationTemplate(context));
    return this;
  },

  setSection: function(section) {
    this.section = section;
    this.render();
  }
});

// Interative visualization of a spider story structure
storybase.viewer.views.Spider = Backbone.View.extend({
  events: {
    "hover g.node": "hoverSectionNode"
  },

  initialize: function() {
    this.sections = this.options.sections;
    this.insertBefore = this.options.insertBefore;
    this.subtractHeight = this.options.subtractHeight;
    this.subtractWidth = this.options.subtractWidth;
    this.activeSection = null;
    // The id for the visualization's wrapper element
    this.visId = 'spider-vis';
    this.maxDepth = null;
    this.sectionsAtDepth = [];
    this.maxSectionsAtDepth = 0;
    this.walkSectionHierarchy(0, this.sections.at(0));
  },

  // Walk the section hierarchy to build a sense of its "shape"
  walkSectionHierarchy: function(depth, section) {
    if (this.maxDepth == null || 
        depth > this.maxDepth) {
      this.maxDepth = depth; 
    } 

    if (this.sectionsAtDepth[depth] === undefined) {
      this.sectionsAtDepth[depth] = 1;
    }
    else {
      this.sectionsAtDepth[depth]++;
    }

    if (this.sectionsAtDepth[depth] > this.maxSectionsAtDepth) {
      this.maxSectionsAtDepth = this.sectionsAtDepth[depth];
    }
    
    var $this = this;
    _.each(section.get('children'), function(childId) {
      $this.walkSectionHierarchy(depth + 1, $this.sections.get(childId));
    });
  },

  // Return the visualization wrapper element
  visEl: function() {
    return this.$('#' + this.visId).first();
  },

  setSection: function(section) {
    this.activeSection = section;
    this.highlightSectionNode(this.activeSection.id);
  },

  highlightSectionNode: function(sectionId) {
    d3.selectAll('g.node').classed('active', false);
    d3.select('g.node.section-' + sectionId).classed('active', true);
  },


  // Get the dimensions of the visualization's wrapper element
  getVisDimensions: function() {
    // We have to calculate the dimensions relative to the window rather than
    // the parent element because the parent element is really tall as it
    // also contains the (hidden) section content.  It seems there should be
    // a better way to do this, but I don't know it.
    width = $(window).width();
    height = $(window).height();
    _.each(this.subtractWidth, function(selector) {
      width -= $(selector).outerWidth();
    });
    _.each(this.subtractHeight, function(selector) {
      height -= $(selector).outerHeight();
    });
    return {
      width: width, 
      height: height 
    };
  },

  // Get the radius of the tree
  getTreeRadius: function(width, height) {
    return (this.maxSectionsAtDepth == 1 ? _.max([width, height]) : _.min([width, height])) * .66;
  },

  render: function() {
    var $this = this;
    var elId = this.$el.attr('id');
    var dimensions = this.getVisDimensions();
    var treeRadius = this.getTreeRadius(dimensions.width, dimensions.height); 
    var vis = d3.select("#" + elId).insert("svg", this.insertBefore)
        .attr("id", this.visId)
        .attr("width", dimensions.width)
        .attr("height", dimensions.height)
	.attr("style", "float:left")
      .append("g");
    var rootSection = this.sections.at(0).populateChildren();
    var tree = d3.layout.tree()
      .size([360, treeRadius - 120])
      .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });
    var diagonal = d3.svg.diagonal.radial()
      .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });
    var nodes = tree.nodes(rootSection);
    // Fix x coordinate (angle) when each level has only one child
    // In this case d.x = NaN which breakins things
    nodes = _.map(nodes, function(node) {
      node.x = $this.maxSectionsAtDepth == 1 ? 90 : node.x;
      return node;
    });
    var links = tree.links(nodes);

    var link = vis.selectAll("path.link")
        .data(links)
      .enter().append("path")
        .attr("class", "link")
        .attr("d", diagonal);

    var node = vis.selectAll("g.node")
      .data(nodes)
      .enter().append("g")
      .attr('class', function(d) {
        return "node section-" + d.id;
      })
      .attr("transform", function(d) { 
	var transform = "";
	if (d.depth > 0) {
	  transform += "rotate(" + (d.x - 90) + ")";
	}
        transform += "translate(" + d.y + ")";
	return transform;
      });

    node.append("circle")
        .attr("r", 15);

    node.append("text")
      .attr("x", function(d) { 
	if (d.depth == 0) { return 20; }
        return d.x < 180 ? 20 : -20; 
      })
      .attr("y", ".31em")
      .attr("text-anchor", function(d) { 
	if (d.depth == 0) { return "start"; }
        return d.x < 180 ? "start" : "end"; })
      .attr("transform", function(d) {
	var rotation = 0;
	if ($this.maxSectionsAtDepth == 1) {
	  rotation = 315;
	}
	else if (d.depth > 0) {
          rotation = 90 - d.x;
	}
	return "rotate(" + rotation + ")"; 
      })
      .text(function(d) { return d.get('title'); });


    // Center the tree within the viewport
    var treeBBox = vis[0][0].getBBox(); 
    var translateX = (0 - treeBBox.x) + ((dimensions.width - treeBBox.width) / 2);
    var translateY = (0 - treeBBox.y) + ((dimensions.height - treeBBox.height) / 2); 
    vis.attr("transform", "translate(" + translateX + ", " + translateY + ")");
  },

  // Event handler for hovering over a section node
  // Changes the cursor to a "pointer" style icon to indicate that
  // the nodes are clickable.
  hoverSectionNode: function(e) {
    e.currentTarget.style.cursor = 'pointer';
  },
});

// Master view that shows a story in a linear fashion
storybase.viewer.views.LinearViewerApp = storybase.viewer.views.ViewerApp.extend({
  elClass: 'linear',

  // Get the position, from the top of the winder, of the lower edge of the
  // header
  headerBottom: function() {
    return this.$('header').offset().top + this.$('header').outerHeight(); 
  },

  footerTop: function() {
    return this.$('footer').offset().top;
  },
	
  // Show the active section
  showActiveSection: function() {
    var sectionTop = this.$('#' + this.activeSection.id).offset().top;
    this._preventScrollEvent = true;
    $(window).scrollTop(sectionTop - this.headerBottom());
  },

  // Return the element of the last visible story section
  getLastVisibleSectionEl: function() {
    var visibleSections = [];
    var numSections = this.$('section').length;
    for (var i = 0; i < numSections; i++) {
      var $section = this.$('section').eq(i);
      var sectionTop = $section.offset().top;
      var sectionBottom = sectionTop + $section.outerHeight(); 
      if (sectionTop >= this.headerBottom() && 
          sectionBottom <= this.footerTop()) { 
        visibleSections.push($section);
      }
    }
    return _.last(visibleSections);
  },

  // Event handler for scroll event
  handleScroll: function(e) {
    var newSection = this.activeSection;
    if (this._preventScrollEvent !== true) {
      if ($(window).scrollTop() == 0) {
	// At the top of the window.  Set the active section to the 
	// first section
	newSection = this.sections.first();
      }
      else {
	var $lastVisibleSectionEl = this.getLastVisibleSectionEl();
	  if ($lastVisibleSectionEl) {
	  var lastVisibleSection = this.sections.get($lastVisibleSectionEl.attr('id'));
	  if (lastVisibleSection != this.activeSection) {
	    newSection = lastVisibleSection; 
	  }
	}
      }
      this.setSection(newSection, {showActiveSection: false});
      storybase.viewer.router.navigate("sections/" + newSection.id,
                                     {trigger: false});
    }
    this._preventScrollEvent = false;
  }
});

// Master view that shows the story structure visualization initially
storybase.viewer.views.SpiderViewerApp = storybase.viewer.views.ViewerApp.extend({
  elClass: 'spider',

  events: {
    "click #topic-map": "clickTopicMapLink",
    "click g.node": "clickSectionNode"
  },

  initialize: function() {
    this.navigationView = new storybase.viewer.views.StoryNavigation({
      addlLinks: [{text: Globalize.localize("Topic Map"), id: 'topic-map'}]
    });
    this.headerView = new storybase.viewer.views.StoryHeader();
    this.initialView = new storybase.viewer.views.Spider({
      el: this.$('#body'),
      sections: this.options.sections,
      insertBefore: '.section',
      subtractWidth: ['.summary'],
      subtractHeight: ['header', 'footer']
    });
    this.sections = this.options.sections;
    this.story = this.options.story;
  },

  render: function() {
    this.$el.addClass(this.elClass);
    this.$('footer').append(this.navigationView.el);
    this.navigationView.render();
    this.initialView.render();
    this.$('.summary').show();
    // Hide all the section content initially
    this.$('.section').hide();
    return this;
  },


  // Show the active section
  showActiveSection: function() {
    // Hide the summary
    this.$('.summary').hide();
    // Hide all sections other than the active one
    this.$('.section').hide();
    this.$('#' + this.activeSection.id).show();
    // Hide the visualization 
    this.initialView.$('svg').hide();
  },

  // Update the active story section in the sub-views
  updateSubviewSections: function() {
    this.navigationView.setSection(this.activeSection);
    this.headerView.setSection(this.activeSection);
    this.initialView.setSection(this.activeSection);
  },

  // Event handler for clicks on a section node
  clickSectionNode: function(e) {
    var node = d3.select(e.currentTarget);
    var sectionId = node.data()[0].id;
    this.initialView.visEl().hide();
    // TODO: I'm not sure if this is the best way to access the router
    // I don't like global variables, but passing it as an argument
    // makes for a weird circular dependency between the master view/
    // router.
    storybase.viewer.router.navigate("sections/" + sectionId,
                                     {trigger: true});
  },

  // Event handler for clicking the "Topic Map" link
  clickTopicMapLink: function(e) {
    this.activeSectionEl().toggle();
    this.initialView.visEl().show();
    this.$('.summary').show();
  }

});

// Get the appropriate master view based on the story structure type
storybase.viewer.views.getViewerApp = function(structureType, options) {
  if (structureType == 'linear') {
    return new storybase.viewer.views.LinearViewerApp(options);
  }
  else if (structureType == 'spider') {
    return new storybase.viewer.views.SpiderViewerApp(options);
  }
  else {
    throw "Unknown story structure type '" + structureType + "'";
  }
};
