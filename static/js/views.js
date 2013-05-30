;(function(_, Backbone, Handlebars, storybase) {
  var HandlebarsTemplateMixin = {
    compileTemplate: function(templateSource) {
      return Handlebars.compile(templateSource);
    },

    compileTemplates: function() {
      this.templates = {};
      var templateSource = this.options.templateSource ? _.result(this.options, 'templateSource') : null;

      if (_.isObject(templateSource)) {
        _.each(this.options.templateSource, function(templateSource, name ) {
          this.templates[name] = this.compileTemplate(templateSource);
        }, this);
      }
      else if (templateSource) {
        this.templates['__main'] = this.compileTemplate(this.options.templateSource); 
      }

      if (this.templates['__main']) {
        this.template = this.templates['__main'];
      }
    },

    getTemplate: function(name) {
      if (name) {
        return this.templates[name];
      }
      else {
        return this.templates['__main'];
      }
    }
  };

  var HandlebarsTemplateView = Backbone.View.extend(
    _.extend({}, HandlebarsTemplateMixin)
  );

  /**
   * Remove the src attribute on selected elements and move its value to a
   * data field named "src". Later, call loadDeferredSrcs on these elements
   * to load them on demand.
   * 
   * @param {hash} [options] {
   *   selector: string or jQuery selection,
   *   scope:    scope for selection
   * }
   */
  var deferSrcLoad = function(options) {
    options = $.extend({
      selector: '*[src]',
      scope: undefined
    }, options);
    $(options.selector, options.scope).each(function() {
      if ($(this).attr('src')) {
        $(this)
          .data('src', $(this).attr('src'))
          .removeAttr('src')
          .addClass('deferred-src')
        ;
      }
    });
  };

  /**
   * When called, selected elements with a data-src attribue will have their 
   * src attribute set to the value of data-src.
   * 
   * @param {hash} [options]  {
   *   selector:  string or jQuery selection
   *   scope:     scope for selection,
   *   force:     boolean; true to overwrite src,
   *   callback:  invoke on element load event, or immediately if element has
   *              a src attribue already
   * }
   */
  var loadDeferredSrcs = function(options) {
    options = $.extend({
      selector: '.deferred-src',
      scope: undefined,
      force: false,
      callback: null
    }, options);
    $(options.selector, options.scope).each(function() {
      var $this = $(this);
      $this.on('load', function() {
        $this.addClass('loaded');
        if (options.callback) {
          options.callback.call(this);
        }
      });
      if (options.force || (!$this.attr('src') && $this.data('src'))) {
        $this.attr('src', $this.data('src'));
      }
      else if ($this.attr('src') && options.callback) {
        // if already loaded (and force is not specified), invoke callback
        options.callback.call(this);
      }
    });
  };
  
  /** 
   * Selectors used as defaults in methods relating to asset autosizing.
   */
  var defaultAssetStructure = {
    containerSelector: 'figure',
    assetSelector: 'iframe, img',
    captionSelector: 'figcaption'
  };
  
  /**
   * Autosize passed iframe element based on its contents. Iframe must be 
   * loaded.
   * 
   * @param {Element|jQuery|String} iframe
   */
  var autoSizeIframe = function(iframe) {
    var iframeContent = $(iframe).prop('contentWindow');
    if (iframeContent) {
      var $body = $('body', iframeContent.document);
      $(iframe)
        .height($body.prop('scrollHeight'))
        .width($body.prop('scrollWidth'))
      ;
    }
  };
  
  /**
   * Autosize an asset. Assumes a structure of asset element in a container 
   * with a sibling caption element. Iframes are sized to fit content. 
   * Container and caption are sized to fit asset. Asset must be loaded.
   * 
   * @param {hash} [options] {
   *   assetSelector:     selector for asset element
   *   containerSelector: selector for asset container element
   *   captionSelector:   selector for asset caption
   * }
   * @param {Element|jQuery} [asset] Asset element to autosize.
   */
  var autosizeAsset = function(options, asset) {
    asset = asset || this;
    options = $.extend(defaultAssetStructure, options);
    var tagName = $(asset).prop('tagName');
    if (tagName && tagName.toLowerCase() == 'iframe') {
      autoSizeIframe(asset);
    }
    // autosize container and caption, if any
    var calculatedWidth = $(asset).width();
    var $container = $(asset).parent(options.containerSelector);
    if ($container) {
      $container.width(calculatedWidth);
      $container.find(options.captionSelector).width(calculatedWidth);
    }
  };
  
  /**
   * Autosize assets when their load event is triggered.
   *
   * @param {hash} [options] {
   *   assetSelector:     selector for asset element,
   *   containerSelector: selector for asset container element,
   *   captionSelector:   selector for asset caption,
   *   scope:             scope element for limiting selectors,
   *   callback:          invoked on each asset following load and autosize
   * }
   */
  var autosizeAssetsOnLoad = function(options) {
    options = $.extend(defaultAssetStructure, {
      scope: undefined,
      callback: null
    }, options);
    $(options.assetSelector, options.scope).each(function() {
      $(this).on('load', function() { 
        autosizeAsset(options, this);
        if (options.callback) {
          options.callback.call(this);
        }
      });
    });
  };
  
  /**
   * Load elements with deferred src attributes (@see {@link deferSrcLoad}). 
   * On load, call {@link autosizeAsset}.
   *
   * @param {hash} [options] {
   *   assetSelector:     selector for asset element,
   *   containerSelector: selector for asset container element,
   *   captionSelector:   selector for asset caption,
   *   scope:             scope element for limiting selectors,
   *   force:             boolean; true to overwrite src,
   *   callback:          invoked on each asset following load and autosize
   * }
   */
  var loadDeferredAssetsAndAutosize = function(options) {
    options = $.extend(defaultAssetStructure, {
      scope: undefined,
      force: false,
      callback: null
    }, options);
    
    loadDeferredSrcs($.extend({}, options, { 
      selector: options.assetSelector,
      callback: function() {
        autosizeAsset(options, this);
        if (options.callback) {
          options.callback.call(this);
        }
      } 
    }));
  };

  storybase.views = storybase.views || {};
  storybase.views.HandlebarsTemplateMixin = HandlebarsTemplateMixin;
  storybase.views.HandlebarsTemplateView = HandlebarsTemplateView;
  storybase.views.deferSrcLoad = deferSrcLoad;
  storybase.views.loadDeferredSrcs = loadDeferredSrcs;
  storybase.views.autoSizeIframe = autoSizeIframe;
  storybase.views.autosizeAsset = autosizeAsset;
  storybase.views.autosizeAssetsOnLoad = autosizeAssetsOnLoad;
  storybase.views.loadDeferredAssetsAndAutosize = loadDeferredAssetsAndAutosize;

})(_, Backbone, Handlebars, storybase);
