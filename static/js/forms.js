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

  getValue: function() {
    // Check if the files property is defined.  It won't be for browsers
    // that don't support the HTML5 File API
    if (this.el.files) {
      // If the File API is supported, return a FILE object
      return this.el.files[0];
    }
    else {
      // Otherwise, return the element value, probably a string
      // representation of the filename.
      return this.$el.val();
    }
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


/**
 * Custom validator for checkboxes.  
 *
 * For whatever reason, 'required' didn't work
 */
storybase.forms.isChecked = function(value, formValues) {
  var err = {
    type: 'checked',
    message: gettext("You must check this checkbox")
  };
  if (!value.length) {
    return err;
  }
};
