(function($) {
  var pluginMethods = {
    init: function(options) {
      this.each(function() {
        var $el = $(this);
        //Drop down
        $el.find('.dd').hide();
        $el.find('ul > li').hover(function(){ 
          $(this).find('.dd:eq(0)').show();
          $(this).find('a:eq(0)').addClass('hover');
          $(this).find('a em').show();
        },
        function(){  
          $(this).find('.dd').hide();
          $(this).find('a:eq(0)').removeClass('hover');
          $(this).find('a em').hide();
        });
      });

      return this;
    }
  };

  $.fn.storybaseMegamenu = function(method) {
    if (pluginMethods[method]) {
      return pluginMethods[method].apply(this, Array.prototype.slice.call(arguments, 1));
    } 
    else if ($.isPlainObject(method) || !method) {
      return pluginMethods.init.apply(this, arguments);
    }
    else {
      $.error('Method ' +  method + ' does not exist on jQuery.storybaseMegamenu');
    }
    
    return this;
  };
})(jQuery);
