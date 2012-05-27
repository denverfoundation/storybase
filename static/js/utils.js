/**
 * Utilities used throughout StoryBase JavaScript apps
 */

Namespace('storybase.utils');

Handlebars.registerHelper('gettext', function(options) {
  return gettext(options.hash.message);
});

/**
 * Pluralize a string
 *
 * Works in manner similar to Django's pluralize filter
 */
Handlebars.registerHelper('pluralize', function(count, options) {
  var suffix;
  var defaults = {
    suffix: "s"
  };
  _.defaults(options.hash, defaults);
  var suffixes = options.hash.suffix.split(",");
  if (suffixes.length == 1) {
    // Only one suffix provided.  This likely means plurals are just
    // formed by appending an 's' to the end of the string and keeping
    // the singular as-is.
    // Fill the singular slot of our options with an empty string
    suffixes.unshift("");
  }
  if (count == 1) {
    suffix = suffixes[0];
  }
  else {
    suffix = suffixes[1];
  }

  return suffix;
});
