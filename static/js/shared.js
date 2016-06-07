(function($) {
  $(document).ready(function() {
    // External links

    $('a').filter(function() {
        return /^https?:\/\//.test($(this).attr('href').toLowerCase());
    }).attr('target', function(index, attr) {
      var href = ($(this).attr('href') || '').toLowerCase();
      if (href.indexOf(document.location.origin) === 0) {
        return attr;
      } else {
        return '_blank';
      }
    });
  });
})(jQuery);
