(function($) {
  
  var defaults = {
    contextForOption: function() {
      return {
        className: $(this).attr('class') || '',
        content: $(this).html() || ''
      };
    },
    markupForContext: function(context) {
      return '<li class="' + context.className + '">' + context.content + '</li>';
    },
    markupForOption: function() {
      return defaults.markupForContext(defaults.contextForOption.apply(this));
    },
    
    cols: 2,
    slideUpDelay: 500
  }; 
  
  var methods = {
    init: function(pluginOptions) {
      pluginOptions = $.extend(defaults, pluginOptions);

      // for each <select> in the jquery selection...
      this.each(function() {
        var $select = $(this);

        var $options = $select.find('option');
        var graphicItems = [];
        var nOptions = $options.length;

        // for each <option> in the select, 
        $options.each(function() {
          var $graphicItem = $(pluginOptions.markupForOption.apply(this));
          $graphicItem.data('graphic-select-option-value', $(this).prop('value'));
          var itemContainerClasses = ['item'];
          if ((graphicItems.length + 1) % pluginOptions.cols == 0) {
            itemContainerClasses.push('last');
          }
          if ((nOptions - graphicItems.length) <= pluginOptions.cols) {
            itemContainerClasses.push('bottom');
          }
          $graphicItem.addClass(itemContainerClasses.join(' '));
          graphicItems.push($graphicItem);
        });

        var $control = $('\
          <div class="graphic-select-container">\
            <div class="widget"><span class="current-selection"></span><span class="arrow"></span></div>\
            <ul class="item-list"></ul>\
          </div>\
        ');

        // update: read <select> state, update state of graphic popup
        var update = $.proxy(function() {
          this.find('.item').removeClass('selected').each(function() {
            var value = $(this).data('graphic-select-option-value');
            var $option = $select.find('option[value=' + value + ']');
            // note: using prop does not seem to update properly
            if ($option.attr('selected')) {
              $(this).addClass('selected');
              $control.find('.widget .current-selection').html($option.html());
            }
          });
        }, $control);


        $.each(graphicItems, function(i, $item) {

          // append graphic items to item list
          $control.find('.item-list').append($item);

          // bind behavior to graphic items
          $item.hover(function() {
            $(this).addClass('hover');
          }, function() {
            $(this).removeClass('hover');
          }).on('click', function() {
            var value = $(this).data('graphic-select-option-value');
            $select.val(value).trigger('change');
            update();
            $('body').off('click.graphicSelect');
            $control.find('.item-list').delay(pluginOptions.slideUpDelay).slideUp('fast');
          });
        });


        // bind behavior to widget
        $control.find('.widget').on('click', function() {
          $control.find('.item-list').slideDown('fast', function() {
            $('body').on('click.graphicSelect', function(event) {
              if ($(event.target).parents('.graphic-select-container').length == 0 || $(event.target).hasClass('widget')) {
                $control.find('.item-list').slideUp('fast');
                $('body').off('click.graphicSelect');
              }
            });
          });
        });

        $control
          .data('graphic-select-original-select', $select)
          .find('.item-list')
            .hide();

        $select
          .data({
            'graphic-select-control': $control,
            'graphic-select-original-display': $select.css('display')
          })
          .css('display', 'none')
          .before($control)
          .on('change', update);

        update();

      });
    },
    remove: function() {
      this.each(function() {
        var $control = $(this).data('graphic-select-control');
        $control.remove();
        $(this).css('display', $(this).data('graphic-select-original-display'));
      });
    }
  };
  
  $.fn.graphicSelect = function(method) {
    if (methods[method]) {
      return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
    } 
    else if ($.isPlainObject(method) || !method) {
      return methods.init.apply(this, arguments);
    }
    else {
      $.error('Method ' +  method + ' does not exist on jQuery.graphicSelect');
    }
    
    return this;
  };
})(jQuery);
