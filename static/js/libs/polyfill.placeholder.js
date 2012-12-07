(function($) {
  function initializePlaceholders() {
    $('[placeholder]').each(function() {
      var input = $(this);
      if (!input.data('polyfill-applied-placeholder')) {
        input
          .focus(function() {
            if (input.val() == input.attr('placeholder')) {
              input.val('');
              input.removeClass('placeholder');
            }
          })
          .blur(function() {
            if (input.val() == '' || input.val() == input.attr('placeholder')) {
              input.addClass('placeholder');
              input.val(input.attr('placeholder'));
            }
          })
          .blur()  // trigger a blur, which initializes the placeholder text 
          .data('polyfill-applied-placeholder', true);  // mark this input as handled
        
        // don't submit placeholder content
        var form = input.parents('form');
        if (!form.data('polyfill-applied-placeholder')) {
          form.submit(function() {
            form.find('[placeholder]').each(function() {
              var input = $(this);
              if (input.val() == input.attr('placeholder')) {
                input.val('');
              }
            })
          }).data('polyfill-applied-placeholder');  // mark form as handled
        }
      }
    });
  }
  
  $(document).ready(function() {
    initializePlaceholders();
    // make it available for running on dynamically-created inputs, as well.
    window.polyfills = window.polyfills || {};
    window.polyfills.placeholders = initializePlaceholders;
  });
})(jQuery)
