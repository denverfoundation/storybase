(function($) {
  
  var defaults = {
    markup: '<h3>Loading&hellip;</h3>',
    storyID: null,
    widgetUrl: '/stories/<id>/share-widget',
    onFetchSuccess: function(data, textStatus, jqXHR) {
      var $button = $(this);
      var $popup = $button.data('share-popup');
      var header = '<header>Sharing Options<span class="close"></span></header>';
      var script = '<script type="text/javascript" src="http://s7.addthis.com/js/250/addthis_widget.js?domready=1"></script>';
      $popup.html(header + data + script);
    },
    onFetchError: function(jqXHR, textStatus, errorThrown) {
      
    },
    onClick: function(event) {
      var $button = $(this);
      $button.data('share-popup').open($button.offset().left, $button.offset().top + $button.outerHeight());
      return false;
    }
  }; 
  
  var popupMethods = {
    open: function(x, y) {
      this
        .css({
          left: x, 
          top: y
        })
        .slideDown()
        .on('click', '.close', this.close);
      //$('body').on('click', ':not(.share-popup *)', this.close);
    },
    close: function() {
      this
        .slideUp()
        .off('click', '.close');
      //$('body').off('click', ':not(.share-popup *)');
    }
  };
  
  var pluginMethods = {
    init: function(pluginOptions) {
      pluginOptions = $.extend(defaults, pluginOptions);
      var plugin = this;
      this.each(function() {
        var $el = $(this);
        var storyID = $el.data('story-id') || pluginOptions.storyID;
        $.ajax({
          url: pluginOptions.widgetUrl.replace('<id>', storyID),
          dataType: 'html',
          success: $.proxy(pluginOptions.onFetchSuccess, this),
          error: $.proxy(pluginOptions.onFetchError, this)
        });
        
        $el.click(pluginOptions.onClick);

        var $body = $el.parents('body');
        $body.append('<div class="share-popup"></div>');
        var $popup = $body.find('.share-popup');
        // this is kind of cheesy. need a better way...
        for (var name in popupMethods) {
          $popup[name] = $.proxy(popupMethods[name], $popup); // note don't use bare element—our jquery obj is what's extended
        }
        $el.data('share-popup', $popup);
      });
    },
    remove: function() {
    }
  };
  
  $.fn.storybaseShare = function(method) {
    if (pluginMethods[method]) {
      return pluginMethods[method].apply(this, Array.prototype.slice.call(arguments, 1));
    } 
    else if ($.isPlainObject(method) || !method) {
      return pluginMethods.init.apply(this, arguments);
    }
    else {
      $.error('Method ' +  method + ' does not exist on jQuery.storybaseShare');
    }
    
    return this;
  };
})(jqLatest);
