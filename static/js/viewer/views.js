/**
 * Views for the story viewer Backbone application
 */
Namespace('storybase.viewer');

// Container view for the viewer application.
// It delegates rendering and events for the entire app to views
// rendering more specific "widgets"
storybase.viewer.views.ViewerApp = Backbone.View.extend({
  options: {
    tocEl: '#toc .story-toc',
    tocButtonEl: '#toggle-toc',
    tocIconEl: '[class^="icon-"]',
    tocOpenClass: 'icon-caret-down',
    tocClosedClass: 'icon-caret-up'
  },

  events: function() {
    var events = {};
    events['click ' + this.options.tocButtonEl] = 'toggleToc';
    events['resize figure img'] = 'handleImgResize';
    return events;
  },

  // Initialize the view
  initialize: function() {
    this.showingConnectedStory = false;
    this.sections = this.options.sections;
    this.story = this.options.story;
    this.navigationView = new storybase.viewer.views.StoryNavigation({
      sections: this.options.sections
    }); 
    // Has the view been rendered yet?
    this._rendered = false;
    // TODO: Decide whether to re-enable updating the section title in the
    // header
    //this.headerView = new storybase.viewer.views.StoryHeader();
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
    this.sizeFigCaptions();
    this.$('.storybase-share-widget').storybaseShare();
    this._rendered = true;
    this.trigger("render");
    return this;
  },

  // Update the active story section in the sub-views
  updateSubviewSections: function() {
    this.navigationView.setSection(this.activeSection);
    
    // highlight TOC entry
    this.$(this.options.tocEl).find('a')
      .removeClass('current')
      .filter('a[href="#sections/' + this.activeSection.id + '"]')
        .addClass('current');

    // TODO: Decide whether to re-enable updating the section title in the
    // header
    //this.headerView.setSection(this.activeSection);
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

  // Convenience method to get the element for the active section
  activeSectionEl: function() {
      return this.activeSection ? this.$('#' + this.activeSection.id) : null;
  },

  // Event handler for scroll event
  handleScroll: function(e) {
    // Do nothing. Subclasses might want to implement this to do some work
  },
  
  sizeFigCaption: function(el) {
    var width = $(el).width();
    this.$(el).next('figcaption').width(width);
    // Resize the figure element as well
    this.$(el).parent('figure').width(width);
  },
  
  sizeFigCaptions: function() {
    // we don't seem to get load events on images
    // even under a hard refresh.
    var view = this;
    this.$('figure img, figure iframe').each(function() {
      if ($(this).width()) {
        view.sizeFigCaption(this);
      }
      // however, set up a handler anyway.
      $(this).on('load', function() {
        view.sizeFigCaption(this);
      });
    });
  },
  
  handleImgResize: function(event) {
    this.sizeFigCaption(event.target);
  },
  
  openToc: function() {
    var $tocEl = $(this.options.tocEl);
    if (!$tocEl.data('open') || _.isUndefined($tocEl.data('open'))) {
      $tocEl.slideDown().data('open', true);
      $(this.options.tocButtonEl)
        .children(this.options.tocIconEl)
        .removeClass(this.options.tocClosedClass)
        .addClass(this.options.tocOpenClass);
      $('body').on('click.toc', $.proxy(function() {
        this.closeToc();
      }, this));
    }
    return false;
  },
  
  closeToc: function() {
    var $tocEl = $(this.options.tocEl);
    if ($tocEl.data('open')) {
      $tocEl.slideUp().data('open', false);
      $(this.options.tocButtonEl)
        .children(this.options.tocIconEl)
        .addClass(this.options.tocClosedClass)
        .removeClass(this.options.tocOpenClass);
      $('body').off('click.toc');
    }
    return false;
  },
  
  toggleToc: function() {
    if ($(this.options.tocEl).data('open')) {
      this.closeToc();
    }
    else {
      this.openToc();
    }
    return false;
  }
});

/**
 * View for the story viewer header.
 *
 * Updates the section heading title when the active section changes
 *
 * Currently unused to conserve vertical space.
 */
/*
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
*/

// View to provide previous/next buttons to navigate between sections
storybase.viewer.views.StoryNavigation = Backbone.View.extend({
  tagName: 'nav',

  id: 'story-nav',

  templateSource: $('#navigation-template').html(),

  initialize: function() {
    this.activeSection = null;
    this.showingConnectedStory = false;
    this.sections = this.options.sections;
    this.template = Handlebars.compile(this.templateSource);
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

  // Render the view
  // Updates the next/previous buttons and where the links point
  render: function() {
    var context = {
      'addl_links': this.addlLinks,
      'showing_connected_story': this.showingConnectedStory
    };

    context.next_section = this.nextSection || null;
    context.previous_section = this.previousSection || null;
    context.totalSectionsNum = this.sections.length;
    context.currentSectionNum = this.sections.models.indexOf(this.activeSection) + 1;
    
    this.$el.html(this.template(context));
    return this;
  },

  // Set the section pointed to by the next button
  setNextSection: function(section) {
    this.nextSection = section ? section : null; 
  },

  // Set the section pointed to by the previous button
  setPreviousSection: function(section) { 
    this.previousSection = section ? section : null;
  },

  // Set the active section of the view 
  setSection: function(section) {
    this.showingConnectedStory = false;
    this.activeSection = section;
    if (this.activeSection) {
      this.setNextSection(this.sections.get(
        this.activeSection.get('next_section_id')
      ));
      this.setPreviousSection(this.sections.get( 	
        this.activeSection.get('previous_section_id')
      ));
    }
    this.render();
  },

  showConnectedStory: function() {
    this.showingConnectedStory = true; 
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
    this.firstSection = this.options.firstSection;
    this.insertBefore = this.options.insertBefore;
    this.subtractHeight = this.options.subtractHeight;
    this.subtractWidth = this.options.subtractWidth;
    this.activeSection = null;
    // The id for the visualization's wrapper element
    this.visId = 'spider-vis';
    this.maxDepth = null;
    this.sectionsAtDepth = [];
    this.maxSectionsAtDepth = 0;
    this.walkSectionHierarchy(0, this.firstSection);
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
    
    var that = this;
    _.each(section.get('children'), function(childId) {
      that.walkSectionHierarchy(depth + 1, that.sections.get(childId));
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
    var that = this;
    var elId = this.$el.attr('id');
    var dimensions = this.getVisDimensions();
    var treeRadius = this.getTreeRadius(dimensions.width, dimensions.height); 
    // Create an SVG element for the spider visualization, attache it to the
    // DOM and set some properties.
    var svg = d3.select("#" + elId).insert("svg", this.insertBefore)
        .attr("id", this.visId)
        .attr("width", dimensions.width)
        .attr("height", dimensions.height)
	.attr("style", "float:left");
    // Create a group inside the SVG element for our visualization
    var vis = svg.append("g");

    // Initialize some attributes used by event handlers
    that.mouseDown = false;

    // Bind some event handlers to the SVG element 
    // It would be nice to use Backbone/jQuery to do this, but
    // it's hard to give the handlers access to both the view
    // object and the d3 event/element
    
    // Disable text selection when we enter the SVG element
    // We need to do this in order to switch the cursor to the 
    // move icon
    svg.on('mouseover', function() {
      document.onselectstart = function() { return false; };
    });

    // Re-enable text selection once we leave the SVG element
    svg.on('mouseout', function() {
      if (!that.mouseDown) {
        document.onselectstart = null;
      }	
    });

    // Bind an event handler for when there's a click inside the SVG element
    svg.on('mousedown', function() {
      // Change the curser icon
      d3.event.target.style.cursor = 'move';
      // Set our flag
      that.mouseDown = true; 
      // Make a record of our present mouse position
      that.pos = d3.svg.mouse(this);
    });

    // Bind an event handler for when the mouse button is released
    d3.select(window).on('mouseup', function() {
      // Unset the flag
      that.mouseDown = false;
      // Change the cursor back to normal
      d3.event.target.style.cursor = 'default';
    });

    // Bind an event handler for moving the mouse within the SVG element
    // This does the heavy lifting for the panning
    svg.on('mousemove', function() {
      svg.on('selectstart', function() { return false; });
      if (that.mouseDown) {
	// Only move things around if the mouse button is held down
	
	// Save the new mouse position
        var currentPos = d3.svg.mouse(this);
	// Calculate how far we've moved since the last recorded mouse
	// position
	var dx = currentPos[0] - that.pos[0];
	var dy = currentPos[1] - that.pos[1];

	// Calculate a new translation of the visualization based on
	// the mouse movement
	var newTranslateX = that.translateX + dx;
	var newTranslateY = that.translateY + dy;

	// Only pan the visualization if it remains partially visible
	// within the SVG element
	if (newTranslateX > 0 && newTranslateY > 0 && 
	    newTranslateX < dimensions.width && newTranslateY < dimensions.height) {
	  that.translateX = newTranslateX;
	  that.translateY = newTranslateY;
          vis.attr("transform", "translate(" + that.translateX + ", " + that.translateY + ")");
	}
	// Update the saved mouse position
	that.pos = currentPos;
      }
    });
    
    var rootSection = this.firstSection.populateChildren();
    var tree = d3.layout.tree()
      .size([360, treeRadius - 120])
      .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });
    var diagonal = d3.svg.diagonal.radial()
      .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });
    var nodes = tree.nodes(rootSection);
    // Fix x coordinate (angle) when each level has only one child
    // In this case d.x = NaN which breakins things
    nodes = _.map(nodes, function(node) {
      node.x = that.maxSectionsAtDepth == 1 ? 90 : node.x;
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
	if (that.maxSectionsAtDepth == 1) {
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
    that.translateX = (0 - treeBBox.x) + ((dimensions.width - treeBBox.width) / 2);
    that.translateY = (0 - treeBBox.y) + ((dimensions.height - treeBBox.height) / 2); 
    vis.attr("transform", "translate(" + that.translateX + ", " + that.translateY + ")");
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

  // override to hook into our own render event.
  initialize: function() {
    this.on('render', this.showActiveSection, this);
    storybase.viewer.views.ViewerApp.prototype.initialize.apply(this, arguments);
  },

  footerTop: function() {
    return this.$('footer').offset().top;
  },
	
  // Show the active section
  showActiveSection: function() {
    var $section = this.$('#' + this.activeSection.id);
    //console.log('show active section: ' + $section.find('h2').html());

    this.showingConnectedStory = false;
    // Hide connected stories
    this.$('.connected-story').hide();
        
    this.$('.section')
      .not($section.show())
      .hide();
  },

  getLastSection: function() {
    return this.$('.section').last();
  },

  showConnectedStory: function(storyId) {
    if (!this._rendered) {
      // The view hasn't been rendered yet.  Wait for this to happen
      // before showing the connected story.  This happens if the
      // a connected story path is accessed directly via the browser's
      // location rather than by clicking on the connected story title in
      // the view
      this.on('render', function() {
        this.showConnectedStory(storyId);
      }, this);
    }
    else {
      this.off('render');
      this.showingConnectedStory = true;
      $(window).scrollTop(0);
      this.$('.section').hide();
      this.$('#connected-story-' + storyId).show();
      this.navigationView.showConnectedStory();
    }
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
    this.sections = this.options.sections;
    var firstSection = this.sections.at(0).id == 'summary' ? this.sections.at(1) : this.sections.at(0);
    this.story = this.options.story;
    this.navigationView = new storybase.viewer.views.StoryNavigation({
      sections: this.options.sections,
      addlLinks: [{text: gettext("Topic Map"), id: 'topic-map'}]
    });
    this.navigationView.setNextSection(firstSection);
    // TODO: Decide whether to re-enable updating the section title in the
    // header
    //this.headerView = new storybase.viewer.views.StoryHeader();
    this.initialView = new storybase.viewer.views.Spider({
      el: this.$('#body'),
      sections: this.options.sections,
      firstSection: firstSection,
      insertBefore: '.section',
      subtractWidth: ['.sidebar'],
      subtractHeight: ['header', 'footer']
    });
  },

  render: function() {
    this.$el.addClass(this.elClass);
    // Create an element for the sidebar 
    $('<div></div>').prependTo(this.$('#body')).addClass('sidebar');
    // Clone the summary and place it in the sidebar
    this.$('#summary').clone().appendTo('.sidebar').removeAttr('id').removeClass('section').show().condense({moreText: gettext("Read more")});
    // Copy the call to action and place it in the sidebar
    this.$('#call-to-action').clone().appendTo('.sidebar').removeAttr('id').removeClass('section').show();
    this.$('footer').append(this.navigationView.el);
    this.navigationView.render();
    this.initialView.render();
    // Hide all the section content initially
    this.$('.section').hide();
    return this;
  },


  // Show the active section
  showActiveSection: function() {
    // Hide the summary
    this.$('.sidebar').hide();
    // Hide all sections other than the active one
    this.$('.section').hide();
    this.$('#' + this.activeSection.id).show();
    // Hide the visualization 
    this.initialView.$('svg').hide();
  },

  // Update the active story section in the sub-views
  updateSubviewSections: function() {
    this.navigationView.setSection(this.activeSection);
    // TODO: Decide whether to re-enable updating the section title in the
    // header
    //this.headerView.setSection(this.activeSection);
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
    var activeSectionEl = this.activeSectionEl();
    if (activeSectionEl !== null) {
      // Only toggle the topic map if an active section has been set
      // The only time there should not be one set is when the viewer 
      // first loads
      activeSectionEl.toggle();
      this.$('.sidebar').toggle();
      var visEl = this.initialView.visEl();
      // $.toggle() doesn't seem to work on the svg element.
      // Toggle the visibility of the element the hard way
      if (visEl.css('display') == 'none') {
	this.initialView.visEl().show();
	// Explicitly set the position of the svg element to accomodate the
	// sidebar
	this.initialView.visEl().css(
	  'left', 
	  this.$('.sidebar').outerWidth()
	);
      }
      else {
	this.initialView.visEl().hide();
      }
    }
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
