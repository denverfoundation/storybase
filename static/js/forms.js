/**
 * Custom editors for backbone-forms
 */
;(function(_, Backbone, storybase) {

  if (_.isUndefined(storybase.forms)) {
    storybase.forms = {};
  }
  var forms = storybase.forms;

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

  /**
   * Update a field's schema definiton with properties
   * relevant to a required field
   */
  storybase.forms.makeRequired = function(fieldDef) {
    var validators = fieldDef.validators || [];
    var fieldClass = fieldDef.fieldClass || '';
    var editorAttrs = fieldDef.editorAttrs || {};

    validators.push('required');
    fieldClass += ' required'; 
    editorAttrs.required = 'required';

    return _.extend(fieldDef, {
      validators: validators,
      fieldClass: fieldClass,
      editorAttrs: editorAttrs
    });
  };

  /**
   * Output text for a form field's label, taking
   * into account whehter or not the field is required.
   */
  storybase.forms.getLabelText = function(s, required) {
    var labelText = s;
    if (required) {
      labelText += " (" + gettext("required") + ")";
    }
    return labelText;
  };
})(_, Backbone, storybase);
