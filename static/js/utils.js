/**
 * Utilities used throughout StoryBase JavaScript apps
 */

Namespace('storybase.utils');

Handlebars.registerHelper('gettext', function(options) {
  return gettext(options.hash.message);
});
