/**
 * Utilities used throughout StoryBase JavaScript apps
 */

Namespace('storybase.utils');

/**
 * Lambda function to call Django's JavaScript version of gettext() on text in
 * templates
 */
storybase.utils.gettext = function() {
  return function(text) {
    return gettext(text);
  }
};

