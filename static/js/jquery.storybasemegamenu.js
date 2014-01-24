(function($) {
  var defaults = {};

  function setWrappedClasses($el) {
    var firstTop = $el.find('ul > li').first().offset().top;
    var wrapped = false;

    $el.find('ul > li').slice(1).each(function() {
      wrapped = ($(this).offset().top !== firstTop); 
      $(this).toggleClass('wrapped', wrapped);
    });

    $el.toggleClass('wrapped', wrapped);

  }

  var methods = {
    init: function(options) {
      var settings = this.settings = $.extend(true, {}, defaults, options);

      this.each(function() {
        var $el = $(this);
        $el.find('.dd').hide();
        $el.find('ul > li').hover(function() { 
          if (!$el.hasClass('visible')) {
            $(this).find('.dd:eq(0)').show();
            $(this).find('a:eq(0)').addClass('hover');
            $(this).find('a em').show();
          }
        },
        function() {  
          if (!$el.hasClass('visible')) {
            $(this).find('.dd').hide();
            $(this).find('a:eq(0)').removeClass('hover');
            $(this).find('a em').hide();
          }
        });

        setWrappedClasses($el);
        $(window).resize(function() {
          setWrappedClasses($el);
        });

        if (settings.toggleButton) {
          settings.toggleButton.click(function(evt) {
            $el.toggleClass('visible');
          });
        }
      });

      return this;
    }
  };

  $.fn.storybaseMegamenu = function(method) {
    if (methods[method]) {
      return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
    } 
    else if ($.isPlainObject(method) || !method) {
      return methods.init.apply(this, arguments);
    }
    else {
      $.error('Method ' +  method + ' does not exist on jQuery.storybaseMegamenu');
    }
    
    return this;
  };
})(jQuery);
