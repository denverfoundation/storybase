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
   * Selectors and other data used as defaults in methods relating to asset
   * sizing.
   */
  var defaultAssetStructure = {
    containerSelector: 'figure',
    assetSelector: 'iframe, img',
    captionSelector: 'figcaption',
    scope: undefined,
    callback: null
  };

  /**
   *
   */
  var sizeImgAsset = function(options) {
    options = $.extend(defaultAssetStructure, options);
    var $img = $(options.assetSelector);
    var $container = $img.parent(options.containerSelector);
    var setSizes = function() {
      var nativeWidth = $img.data('native-width');
      if ($container.width() < nativeWidth) {
        $container.width('auto');
      }
      else {
        $container.width(nativeWidth);
      }
      if (options.callback) {
        options.callback.apply(this);
      }
    };
    setDataNativeImgSize({
      selector: $img,
      callback: setSizes
    });
  };

  /**
   * Size passed iframe element based on its contents. Size its container
   * and caption to match. Iframe must be loaded.
   *
   * @param {hash} options @see {@link defaultAssetStructure}.
   */
  var sizeIframeAsset = function(options) {
    options = $.extend(defaultAssetStructure, options);
    var iframe = $(options.assetSelector, options.scope);
    if (iframe) {
      var iframeContent = $(iframe).prop('contentWindow');
      if (iframeContent) {
        var $body = $('body', iframeContent.document);
        $(iframe)
          .height($body.prop('scrollHeight'))
          .width($body.prop('scrollWidth'))
        ;
        var calculatedWidth = $(iframe).width();
        var $container = $(iframe).parent(options.containerSelector);
        if ($container) {
          $container.width(calculatedWidth);
          $container.find(options.captionSelector).width(calculatedWidth);
        }
      }
      if (options.callback) {
        options.callback.apply(iframe);
      }
    }
  };

  /**
   * Size an asset. Assumes a structure of asset element in a container
   * with a sibling caption element. Iframes are sized to fit content.
   * Imgs are sized to fill container unless filling would require upsampling.
   * Container and caption are sized to fit asset. Asset must be loaded.
   *
   * @param {hash} options @see {@link defaultAssetStructure}.
   * }
   */
  var sizeAsset = function(options) {
    options = $.extend(defaultAssetStructure, options);
    var $asset = $(options.assetSelector, options.scope);
    if ($asset.length) {
      switch ($asset.prop('tagName').toLowerCase()) {
      case 'iframe':
        sizeIframeAsset(options);
        break;
      case 'img':
        sizeImgAsset(options);
        break;
      }
    }
  };

  /**
   * Run sizing logic on selected assets.
   *
   * @param {hash} options @see {@link defaultAssetStructure}.
   */
  var sizeAssets = function(options) {
    options = $.extend(defaultAssetStructure, options);
    $(options.assetSelector, options.scope).each(function() {
      sizeAsset($.extend(options, {
        assetSelector: this
      }));
    });
  };

  /**
   * Size assets when their load event is triggered.
   *
   * @param {hash} options @see {@link defaultAssetStructure}.
   */
  var sizeAssetsOnLoad = function(options) {
    options = $.extend(defaultAssetStructure, options);
    $(options.assetSelector, options.scope).each(function() {
      if ($(this).prop('tagName').toLowerCase() == 'img') {
        $(this).imagesLoaded(function() {
          sizeAsset($.extend(options, {
            assetSelector: this
          }));
        });
      }
      else {
        $(this).on('load', function() {
          sizeAsset($.extend(options, {
            assetSelector: this
          }));
        });
      }
    });
  };

  /**
   * Load elements with deferred src attributes (@see {@link deferSrcLoad}).
   * On load, call {@link sizeAsset}.
   *
   * @param {hash} options @see {@link defaultAssetStructure}, with addition
   * of `force` key to pass to {@link loadDeferredSrcs}.
   */
  var loadDeferredAssetsAndSize = function(options) {
    options = $.extend(defaultAssetStructure, {
      force: false,
    }, options);

    loadDeferredSrcs($.extend({}, options, {
      selector: options.assetSelector,
      callback: function() {
        sizeAsset($.extend(options, {
          assetSelector: this
        }));
      }
    }));
  };

  /**
   * Mark selected img elements with data:
   *  native-width
   *  native-height
   *
   * Ping a callback when data is available. Will invoke callback
   * immediately for elements that already have those data set.
   *
   * @param {hash} [options] {
   *   selector:          selector for img elements,
   *   scope:             scope element for limiting selectors,
   *   callback:          invoked once per img when data is available
   * }
   */
  var setDataNativeImgSize = function(options) {
    options = $.extend({
      selector: 'img',
      scope: undefined,
      callback: null
    }, options);
    $(options.selector, options.scope).each(function() {
      var $img = $(this);
      if (_.isUndefined($img.data('native-width'))) {
        // we don't know native size yet
        var $copy = $(new Image());
        $copy.prop('src', $img.prop('src'));
        $copy.imagesLoaded(function() {
          $img.data({
            'native-width': $copy.prop('width'),
            'native-height': $copy.prop('height')
          });
          $copy.remove();
          if (options.callback) {
            options.callback.call(this);
          }
        });
      }
      else {
        // native size already set; just trigger the callback
        if (options.callback) {
          options.callback.call(this);
        }
      }
    });
  };


  storybase.views = storybase.views || {};
  storybase.views.HandlebarsTemplateMixin = HandlebarsTemplateMixin;
  storybase.views.HandlebarsTemplateView = HandlebarsTemplateView;
  storybase.views.deferSrcLoad = deferSrcLoad;
  storybase.views.loadDeferredSrcs = loadDeferredSrcs;
  storybase.views.sizeAsset = sizeAsset;
  storybase.views.sizeAssets = sizeAssets;
  storybase.views.sizeAssetsOnLoad = sizeAssetsOnLoad;
  storybase.views.loadDeferredAssetsAndSize = loadDeferredAssetsAndSize;

})(_, Backbone, Handlebars, storybase);
