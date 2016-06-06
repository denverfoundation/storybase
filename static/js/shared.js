(function($) {
  $(document).ready(function() {
    // External links
    $('a[href^="http://" i], a[href^="https://"] i').attr('target', function(index, attr) {
      var href = ($(this).attr('href') || '').toLowerCase();
      if (href.indexOf(document.location.origin) === 0) {
        return attr;
      } else {
        return '_blank';
      }
    });
  });
})(jQuery);
