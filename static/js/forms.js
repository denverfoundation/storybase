/**
 * Custom editors for backbone-forms
 */

Namespace('storybase.forms');

storybase.forms.File = Backbone.Form.editors.Text.extend({
  initialize: function(options) {
    editors.Base.prototype.initialize.call(this, options);

    this.$el.attr('type', 'file');
  }
});
