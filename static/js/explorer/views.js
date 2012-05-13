/**
 * Views for the story explorer Backbone application
 */
Namespace('storybase.explorer');

storybase.explorer.views.ExplorerApp = Backbone.View.extend({
  el: $('#explorer'),

  templateSource: $('#explorer-template').html(),

  initialize: function() {
    this.storyData = this.options.storyData;
    this.template = Handlebars.compile(this.templateSource);
    this.filterView = new storybase.explorer.views.Filters({
      topics: this.storyData.topics,
      organizations: this.storyData.organizations,
      projects: this.storyData.projecs,
      languages: this.storyData.languages
    });
  },

  render: function() {
    var context = {
      gettext: storybase.utils.gettext
    };
    this.$el.html(this.template(context));
    this.filterView.render();
    this.$el.prepend(this.filterView.el);
    return this;
  }
});

storybase.explorer.views.Filters = Backbone.View.extend({
  tagName: 'div',

  id: 'filters',

  templateSource: $('#filters-template').html(),

  initialize: function() {
    this.template = Handlebars.compile(this.templateSource);
  },

  render: function() {
    var context = {
      topics: this.options.topics,
      organizations: this.options.organizations,
      projects: this.options.projects,
      languages: this.options.languages,
      gettext: storybase.utils.gettext
    }
    this.$el.html(this.template(context));
    return this;
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
       gettext: storybasse.utils.getext,
       stories: this.stories
    }
    this.$el.html(this.template(context));
    return this;
  }
});
