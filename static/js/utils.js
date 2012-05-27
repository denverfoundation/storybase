/**
 * Utilities used throughout StoryBase JavaScript apps
 */

Namespace('storybase.utils');

/**
 * Translate a string in a template using Django's gettext Javascript API.
 * @param {object} options Hash of options. Should contain one key,
 *     'message' which is the string to be translated.
 * @return {string} Translated string
 */
Handlebars.registerHelper('gettext', function(options) {
  return gettext(options.hash.message);
});

/**
 * Translate a block of template text after first rendering the
 * contents of the template.
 * @return {string} Translated block of text
 */
Handlebars.registerHelper('blockgettext', function(options) {
  return gettext(options.fn(this));
});

/**
 * Return a singular or plural suffix
 * Works in a manner similar to Django's pluralize filter
 * @param {number} count The number used to determine if the singular or
 *    plural suffix should be returned.
 * @param {object} options Hash of options. Optionally contains one key,
 *     'suffix' which is either the plural suffix (e.g. 's') or a
 *     comma-separated list of the singular and plural suffixes
 *     (e.g. 'y,ies')
 * @return {string} Suffix
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
