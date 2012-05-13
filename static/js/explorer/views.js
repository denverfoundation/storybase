/**
 * Views for the story explorer Backbone application
 */
Namespace('storybase.explorer');

storybase.explorer.views.ExplorerApp = Backbone.View.extend({
  el: $('#explorer'),

  templateSource: $('#explorer-template').html(),

  initialize: function() {
    this.stories = new storybase.collections.Stories;
    this.stories.reset(this.options.storyData.objects);
    console.debug(this.stories.toJSON());
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
  },

  render: function() {
    var context = {
    };
    this.$el.html(this.template(context));
    this.filterView.render();
    this.$el.prepend(this.filterView.el);
    this.storyListView.render();
    this.$el.append(this.storyListView.el);
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
       stories: this.stories.toJSON()
    }
    this.$el.html(this.template(context));
    return this;
  }
});
