(function() {
  var root = this;
  root.storybase = root.storybase || {};
  var widgets = root.storybase.widgets = root.storybase.widgets || {};
  if (widgets.showWidgets) {
    // The storybase.widgets object has already been defined,
    // meaning this script has already been loaded. Just process the
    // remaining placeholders and exit.
    widgets.showWidgets();
    return;
  }

  // Get the base URL for the site that serves the widget content
  var getBaseUrl = function() {
    var baseUrl;
    // This script will be the last script on the page
    var scripts = document.getElementsByTagName('script');
    var index = scripts.length - 1;
    var scriptUrl = scripts[index].src;
    // To easily parse the URL, assign the script src string to the href
    // property of an '<a>' element
    var l = document.createElement("a");
    l.href = scriptUrl;
    var detectedUrl = '//' + l.host;
    return root._sbBaseUrl || detectedUrl || 'https://floodlightproject.org';
  };

  // Polyfill for String.trim
  var trim = function(s) {
    if (typeof(String.prototype.trim) === "undefined") {
      return s.replace(/^\s\s*/, '').replace(/\s\s*$/, '');
    }
    else {
      return s.trim();
    }
  };

  /*
	Developed by Robert Nyman, http://www.robertnyman.com
	Code/licensing: http://code.google.com/p/getelementsbyclassname/
  */	
  var getElementsByClassName = function (className, tag, elm){
    if (document.getElementsByClassName) {
      getElementsByClassName = function (className, tag, elm) {
        elm = elm || document;
        var elements = elm.getElementsByClassName(className),
          nodeName = (tag)? new RegExp("\\b" + tag + "\\b", "i") : null,
          returnElements = [],
          current;
        for(var i=0, il=elements.length; i<il; i+=1){
          current = elements[i];
          if(!nodeName || nodeName.test(current.nodeName)) {
            returnElements.push(current);
          }
        }
        return returnElements;
      };
    }
    else if (document.evaluate) {
      getElementsByClassName = function (className, tag, elm) {
        tag = tag || "*";
        elm = elm || document;
        var classes = className.split(" "),
          classesToCheck = "",
          xhtmlNamespace = "http://www.w3.org/1999/xhtml",
          namespaceResolver = (document.documentElement.namespaceURI === xhtmlNamespace)? xhtmlNamespace : null,
          returnElements = [],
          elements,
          node;
        for(var j=0, jl=classes.length; j<jl; j+=1){
          classesToCheck += "[contains(concat(' ', @class, ' '), ' " + classes[j] + " ')]";
        }
        try	{
          elements = document.evaluate(".//" + tag + classesToCheck, elm, namespaceResolver, 0, null);
        }
        catch (e) {
          elements = document.evaluate(".//" + tag + classesToCheck, elm, null, 0, null);
        }
        while ((node = elements.iterateNext())) {
          returnElements.push(node);
        }
        return returnElements;
      };
    }
    else {
      getElementsByClassName = function (className, tag, elm) {
        tag = tag || "*";
        elm = elm || document;
        var classes = className.split(" "),
          classesToCheck = [],
          elements = (tag === "*" && elm.all)? elm.all : elm.getElementsByTagName(tag),
          current,
          returnElements = [],
          match;
        for(var k=0, kl=classes.length; k<kl; k+=1){
          classesToCheck.push(new RegExp("(^|\\s)" + classes[k] + "(\\s|$)"));
        }
        for(var l=0, ll=elements.length; l<ll; l+=1){
          current = elements[l];
          match = false;
          for(var m=0, ml=classesToCheck.length; m<ml; m+=1){
            match = classesToCheck[m].test(current.className);
            if (!match) {
              break;
            }
          }
          if (match) {
            returnElements.push(current);
          }
        }
        return returnElements;
      };
    }
    return getElementsByClassName(className, tag, elm);
  };

  var hasClass = function hasClass(el, cls) {
    return (' ' + el.className + ' ').indexOf(' ' + cls + ' ') > -1;
  };
 
  /**
   * Return the URL suitable for the src attribute of the widget iframe
   *
   * @param {HtmlElement} el Element that will be replaced by the widget
   * @param {String} baseWidgetUrl URL of page that serves the widget content
   * @param {Object} opts Options for the widget URL
   * @param {String} [opts.version] Widget version 
   */ 
  var getUrl = function(el, baseWidgetUrl, opts) {
    var url = el.getAttribute('href');
    var queryArgs = [];
    var widgetUrl = baseWidgetUrl; 
    var storyUrl, listUrl;

    // Lazily catch exceptions and return the default widget URL
    // This helps ensure that we always render *something*
    // This should be cheaper than checking for exceptions more
    // locally
    try {
      if (!url) {
        // No URL, assume story + list style embed
        storyUrl = getElementsByClassName('storybase-story', null, el)[0].getAttribute('href');
        storyUrl = storyUrl ? trim(storyUrl) : storyUrl; 
        listUrl = getElementsByClassName('storybase-list', null, el)[0].getAttribute('href');
        listUrl = listUrl ? trim(listUrl) : listUrl; 
      }

      if (url) {
        url = url ? trim(url) : url;
        url = url[url.length - 1] === '/' ? url : url + '/';
        if (hasClass(el, 'storybase-story-embed')) {
          storyUrl = url;
        }
        else if (hasClass(el, 'storybase-list-embed')) {
          listUrl = url;
        }
      }

      if (storyUrl) {
        queryArgs.push('story-url=' + encodeURIComponent(storyUrl));
      }

      if (listUrl) {
        queryArgs.push('list-url=' + encodeURIComponent(listUrl));
      }

      widgetUrl = opts.version ? widgetUrl + opts.version + '/' : widgetUrl;
      if (queryArgs.length) {
        widgetUrl = widgetUrl + '?' + queryArgs.join('&');
      }
    }    
    catch (e) {
      // Do nothing, just return the default value of widgetUrl
      // below
    }

    return widgetUrl;
  }; 

  var showWidgets = widgets.showWidgets = function(baseUrl) {
    baseUrl = baseUrl || getBaseUrl();
    var baseWidgetUrl = baseUrl + '/widget/';
    var phs = getElementsByClassName('storybase-story-embed')
      .concat(getElementsByClassName('storybase-list-embed'))
      .concat(getElementsByClassName('storybase-story-list-embed'));
    var defaults = {
      height: '500px',
      width: '600px',
      version: null
    };
    var i, ph, el, url, opts, height, version;

    for (i = 0; i < phs.length; i++) {
      opts = {};
      ph = phs[i];
      if (ph.style.display != 'none') {
        // Only process visible elements as we assume elements with
        // display:none have already been processed
        opts.height = ph.getAttribute('data-height') || defaults.height;
        opts.width = ph.getAttribute('data-width') || defaults.width;
        opts.version = ph.getAttribute('data-version') || defaults.version; 
        url = getUrl(ph, baseWidgetUrl, opts);
        if (url) {
          el = document.createElement('iframe');
          el.setAttribute('name', 'storybase-story-widget-frame');
          el.setAttribute('src', url);
          el.setAttribute('style', "border: none; height: " + opts.height + "; width: " + opts.width + ";");
          ph.parentNode.insertBefore(el, ph);
          ph.style.display = 'none';
        }
      }
    }
  };
  showWidgets(); 
}).call(this);
