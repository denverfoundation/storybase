(function(_, Backbone, Handlebars, storybase) {
  var HandlebarsTemplateMixin = {
    compileTemplate: function(templateSource) {
      return Handlebars.compile(templateSource);
    },

    compileTemplates: function() {
      this.templates = {};
      var templateSource = this.options.templateSource ? _.result(this.options, 'templateSource') : null;

      if (_.isObject(templateSource)) {
        _.each(this.options.templateSource, function(templateSource, name ) {
          this.templates[name] = this.compileTemplate(templateSource);
        }, this);
      }
      else if (templateSource) {
        this.templates['__main'] = this.compileTemplate(this.options.templateSource); 
      }

      if (this.templates['__main']) {
        this.template = this.templates['__main'];
      }
    },

    getTemplate: function(name) {
      if (name) {
        return this.templates[name];
      }
      else {
        return this.templates['__main'];
      }
    }
  };

  var HandlebarsTemplateView = Backbone.View.extend(
    _.extend({}, HandlebarsTemplateMixin)
  );

  storybase.views = storybase.views || {};
  storybase.views.HandlebarsTemplateMixin = HandlebarsTemplateMixin;
  storybase.views.HandlebarsTemplateView = HandlebarsTemplateView;
})(_, Backbone, Handlebars, storybase);
