/**
 * Views for the story viewer Backbone application
 */
Namespace('storybase.viewer');

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
    this.setSection(this.sections.at(0));
  },

  // Add the view's container element to the DOM and render the sub-views
  render: function() {
    this.$('footer').append(this.navigationView.el);
    this.navigationView.render();
    return this;
  },

  // Update the active story section in the sub-views
  updateSubviewSections: function() {
    this.navigationView.setSection(this.currentSection);
    this.headerView.setSection(this.currentSection);
  },

  // Set the active story section
  setSection: function(section) {
    this.currentSection = section;
    this.updateSubviewSections();
  },

  // Like setSection(), but takes a section ID as an argument instead of
  // a Section model instance object
  setSectionById: function(id) {
    this.setSection(this.sections.get(id));
  },

  // Convenience method to get the element for the active
  activeSectionEl: function() {
    return this.$('#' + this.currentSection.id);
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
    context.next_section = this.section.collection.get(
      this.section.get('next_section_id'));
    context.previous_section = this.section.collection.get(
      this.section.get('previous_section_id'));
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
    // The id for the visualization's wrapper element
    this.visId = 'spider-vis';
  },

  // Return the visualization wrapper element
  visEl: function() {
    return this.$('#' + this.visId).first();
  },

  render: function() {
    var elId = this.$el.attr('id');
    var width = this.$el.width(); 
    var height = this.$el.height(); 
    var vis = d3.select("#" + elId).insert("svg", "section")
        .attr("id", this.visId)
        .attr("width", width)
        .attr("height", height)
      .append("g")
      .attr("transform", "translate(40, 100)");
    var rootSection = this.sections.at(0).populateChildren();
    var tree = d3.layout.tree().size([300, 150]);
    var diagonal = d3.svg.diagonal();
    var nodes = tree.nodes(rootSection);
    var links = tree.links(nodes);

    var link = vis.selectAll("path.link")
        .data(links)
      .enter().append("path")
        .attr("class", "link")
        .attr("d", diagonal);

    var node = vis.selectAll("g.node")
      .data(nodes)
      .enter().append("g")
      .attr("class", "node")
      .attr("transform",function(d) { return "translate(" + d.x + "," + d.y + ")"; });

    node.append("circle")
        .attr("r", 10);

    node.append("text")
      .attr("dx", function(d) { return d.children ? -20 : 20; })
      .attr("dy", 3)
      .attr("text-anchor", function(d) { return d.children ? "end" : "start"; }) 
      .text(function(d) { return d.get('title'); })

  },

  // Event handler for hovering over a section node
  // Changes the cursor to a "pointer" style icon to indicate that
  // the nodes are clickable.
  hoverSectionNode: function(e) {
    e.currentTarget.style.cursor = 'pointer';
  },
});

// Master view that shows the story structure visualization initially
storybase.viewer.views.SpiderViewerApp = storybase.viewer.views.ViewerApp.extend({
  events: {
    "click #topic-map": "clickTopicMapLink",
    "click g.node": "clickSectionNode"
  },

  initialize: function() {
    this.navigationView = new storybase.viewer.views.StoryNavigation({
      addlLinks: [{text: "Topic Map", id: 'topic-map'}]
    });
    this.headerView = new storybase.viewer.views.StoryHeader();
    this.initialView = new storybase.viewer.views.Spider({
      el: this.$('#body'),
      sections: this.options.sections
    });
    this.sections = this.options.sections;
    this.story = this.options.story;
    this.setSection(this.sections.at(0));
  },

  render: function() {
    this.$('footer').append(this.navigationView.el);
    this.navigationView.render();
    this.initialView.render();
    return this;
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
  }

});

// Get the appropriate master view based on the story structure type
storybase.viewer.views.getViewerApp = function(structureType, options) {
  if (structureType == 'linear') {
    return new storybase.viewer.views.ViewerApp(options);
  }
  else if (structureType == 'spider') {
    return new storybase.viewer.views.SpiderViewerApp(options);
  }
  else {
    throw "Unknown story structure type '" + structureType + "'";
  }
};
