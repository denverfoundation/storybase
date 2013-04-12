/**
 * Namespace and globals for storybase Backbone apps
 */
;(function() {
  var root = this;
  var storybase;
  if (_.isUndefined(root.storybase)) {
    root.storybase = {};
  }
  storybase = this.storybase;

  if (_.isUndefined(storybase.globals)) {
    storybase.globals = {};
  }
}).call(this);
