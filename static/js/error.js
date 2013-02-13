/**
 * Handle uncaught JavaScript exceptions.
 */
;(function(window, document, undefined) {
  function errorPopup() {
    var errorBox = document.createElement("div");
    errorBox.className = 'error-popup';
    errorBox.innerHTML = "There was an unexpected error. You should try to reload the page while <a href='http://wikipedia.org/wiki/Wikipedia:Bypass_your_cache' title='Bypass your cache' onclick='window.open(this.href);return false;'>bypassing the cache</a>. If that doesn't fix the error, <a href='/contact/' title='Contact' onclick='window.open(this.href);return false;'>tell us what happened</a>.";
    document.body.appendChild(errorBox);
    return false;
  }

  window.onerror = function(message, url, lineNumber) {
    return errorPopup();
  };
})(window, document);
