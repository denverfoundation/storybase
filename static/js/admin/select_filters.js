/**
 * Functions for dynamically setting Select2-enabled select elements
 * that are populated with AJAX calls.
 */

(function($) {
/**
 * Filter a place's parent selection element based on the place's geolevel
 *
 * Filters the results to only places that are at the place's geolevel's
 * parent
 */
  storybase.admin.selectFilters = {
    geoLevelFilters: function(filters) {
      var geoLevel = $('#id_geolevel').val();
      var newFilters = {};
      if (geoLevel !== "") {
        $.ajax({
          async: false,
          url: "/api/0.1/geolevels/",
          dataType: 'json',
          data: {
            'id': geoLevel
          },
          success: function(data) {
            // If the place's geolevel doesn't have a parent, set the 
            // filter id to 0 which should always return an empty list
            var parentId = data.objects[0].parent_id !== null ? data.objects[0].parent_id : 0;
            newFilters['geolevel__id'] = parentId;
          }
        });
      }
      else {
        // No geoLevel has been selected.  Set the filter ID to 0 which
        // should always return an empty list
        newFilters['geolevel__id'] = 0;
      }

      $.extend(filters, newFilters);
    }
  };

  storybase.admin.callSelectFilter = function(name, filters) {
    storybase.admin.selectFilters[name](filters);
  };
})(django.jQuery);
