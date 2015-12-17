/**
 * Namespace, globals and a few universally used functions
 */
;(function($) {
  var root = this;
  if (root.storybase === void 0) {
    root.storybase = {};
  }
  var storybase = this.storybase;

  // TODO: Use this instead of similar handlers elsewhere in the code
  /**
   * Click handler that opens a link in a new window
   */
  storybase.openInNewWindow = function(evt) {
    evt.preventDefault();
    var url = $(evt.currentTarget).attr('href');
    var windowName = $(evt.target).data('window-name') || '_blank';
    var windowFeatures = $(evt.target).data('window-features');

    // In Firefox, if windowFeatures is passed, the new window will be
    // in a window rather than a tab. Generally, we want to open things
    // in a new tab, so only pass the third argument if it's truthy
    if (windowFeatures) {
      window.open(url, windowName, windowFeatures);
    }
    else {
      window.open(url, windowName);
    }
    return false;
  };
}).call(this, jQuery);
