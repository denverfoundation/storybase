/**
 * Namespace, globals and a few universally used functions
 */
;(function($) {
  var root = this;
  if (root.storybase === void 0) {
    root.storybase = {};
  }
  var storybase = this.storybase;

  /**
   * Click handler that opens a link in a new window
   */
  storybase.openInNewWindow = function(evt) {
    // TODO: Use this instead of similar handlers elsewhere in the code
    evt.preventDefault();
    var url = $(evt.currentTarget).attr('href'); 
    var windowName = $(evt.target).data('window-name') || '_blank';
    var windowFeatures = $(evt.target).data('window-features');
    window.open(url, windowName, windowFeatures);
    return false;
  };
}).call(this, jQuery);
