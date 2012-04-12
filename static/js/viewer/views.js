/**
 * Views for the story viewer Backbone application
 */
Namespace('storybase.viewer');

storybase.viewer.views.ViewerApp = Backbone.View.extend({
  events: {
  },

  initialize: function() {
    this.navigationView = new storybase.viewer.views.StoryNavigation(); 
    this.headerView = new storybase.viewer.views.StoryHeader();
    /*
    this.initialView = new storybase.viewer.views.Spider({
      el: this.$('#body'),
      sections: this.options.sections
    });
    */
    this.sections = this.options.sections;
    this.story = this.options.story;
    this.setSection(this.sections.at(0));
  },

  render: function() {
    this.$('footer').append(this.navigationView.el);
    this.navigationView.render();
    //this.initialView.render();
    return this;
  },

  updateSubviewSections: function() {
    this.navigationView.setSection(this.currentSection);
    this.headerView.setSection(this.currentSection);
  },

  setSection: function(section) {
    this.currentSection = section;
    this.updateSubviewSections();
  },

  setSectionById: function(id) {
    this.setSection(this.sections.get(id));
  },
});

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

storybase.viewer.views.StoryNavigation = Backbone.View.extend({
  tagName: 'nav',

  className: 'story-nav',

  render: function() {
    var nextSection = this.section.collection.get(
      this.section.get('next_section_id'));
    var prevSection = this.section.collection.get(
      this.section.get('previous_section_id'));
    this.$el.html(ich.navigationTemplate({
      next_section: nextSection,
      previous_section: prevSection
    }));
    return this;
  },

  setSection: function(section) {
    this.section = section;
    this.render();
  }
});

storybase.viewer.views.Spider = Backbone.View.extend({
  initialize: function() {
    this.sections = this.options.sections;
  },

  render: function() {
    var elId = this.$el.attr('id');
    var width = 500;
    var height = 500;
    var centerX = width / 2;
    var centerY = height / 2;
    var circleR = 10;
    var circlePadding = 5;
    var svg = d3.select("#" + elId).insert("svg", "section").attr("width", width).attr("height", height);

    var numSections = this.sections.length;
    for (var i = 0; i < numSections; i++) {
      section = this.sections.at(i);
      var cx;
      var offset = ((numSections - i) * circleR) + (2 * circlePadding);
      if (i < (numSections / 2)) {
        cx = centerX - offset;
      }
      else {
        cx = centerX + offset;
      }
      svg.append("circle")
         .attr("id", "circle-" + section.id)
         .attr("cx", cx)
         .attr("cy", centerY)
         .attr("r", circleR);

    }
    
  }
});
