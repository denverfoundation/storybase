/**
 * Helper functions and methods for Jasmine specs.
 */
beforeEach(function() {
  /**
   * Generate a valid JSON response for our fake server
   *
   * Taken from http://tinnedfruit.com/2011/03/25/testing-backbone-apps-with-jasmine-sinon-2.html
   */
  this.validResponse = function(responseText) {
    return [
      200,
      {"Content-Type": "application/json"},
      JSON.stringify(responseText)
    ];
  };
});
