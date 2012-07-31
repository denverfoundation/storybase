/**
 * Custom editors for backbone-forms
 */

Namespace('storybase.forms');

Backbone.Form.setTemplates({
  noLabelField: '\
    <li class="bbf-field field-{{key}}">\
      <div class="bbf-editor">{{editor}}</div>\
      <div class="bbf-help">{{help}}</div>\
    </li>\
  ',
});

storybase.forms.RichTextEditorMixin = {
  toolbarTemplateSource: $('#editor-toolbar-template').html(),

  getEditorToolbarHtml: function() {
    return this.toolbarTemplateSource; 
  },

  getEditorToolbarEl: function() {
    if (_.isUndefined(this._editorToolbarEl)) {
      this._editorToolbarEl = $(this.getEditorToolbarHtml())[0];
    }
    return this._editorToolbarEl; 
  }

};

storybase.forms.File = Backbone.Form.editors.Text.extend({
  initialize: function(options) {
    Backbone.Form.editors.Base.prototype.initialize.call(this, options);

    this.$el.attr('type', 'file');
  },

  /**
   * Set the editor value.
   *
   * This version doesn't do anything because the browser doesn't
   * let you set the value of a file input for security reasons.
   */
  setValue: function(value) {
  },
 
  /**
   * Retrieve the file selected in this input as a data URL
   */
  getValueAsDataURL: function(loadCallback, errorCallback) {
    var file = this.el.files[0];
    if (file) {
      var reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = function(evt) {
        loadCallback(evt.target.result);
      };
    }
  }
});
