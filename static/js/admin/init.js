/**
 * Initialization for custom admin Javascript for StoryBase
 */

/**
 * Make django.jQuery available as jQuery so plugins can find
 * it.
 */
if (typeof jQuery === "undefined") {
  jQuery = django.jQuery;
}

/**
 * Create a custom namespace
 */
storybase = {
  admin: {}
};

