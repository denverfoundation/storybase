;(function($) {
  var defaults = {
    containerClassName: 'activities-container',
    containerSel: '.activities-container'
  };

  $.fn.storybaseActivityGuide = function(options) {
    var $activityBlocks = this;
    var settings = $.extend(defaults, options);
    var $container = settings.container;
    if ($container && typeof selector === "string") {
      // container was specified as an option, but it's a string, not a jQuery
      // object.  Use the value as a selector to get a jQuery object
      $container = $($container);
    }

    this.each(function() {
      var $el = $(this);
      if (!$container) {
        // We couldn't match a container.  Create a new element before the first
        // matched element.
        $container = $('<div>').addClass(settings.containerClassName).insertBefore($el);
      }
      $el.addClass('is-collapsed').appendTo($container).find('.toggle').click(function() {
        // Close any expanded boxes other than this one
        $activityBlocks.filter('.is-expanded').not($el).removeClass('is-expanded').addClass('is-collapsed');
        $activityBlocks.find('.toggle.icon-minus').not(this).removeClass('icon-minus').addClass('icon-plus');
        $(this).toggleClass('icon-plus icon-minus');
        $el.toggleClass('is-collapsed is-expanded');

        // Refresh the masonry to fill any gaps created by the expanded element
        $container.masonry('reload');
        return false;
      });
    });

    $container.masonry({
      itemSelector: this.selector
    });

    return this;
  };
})(jQuery);
