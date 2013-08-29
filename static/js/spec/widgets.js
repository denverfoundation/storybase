describe('Embed widget', function() {
  describe('showWidgets function', function() {
    _.templateSettings = {
        interpolate : /\{\{(.+?)\}\}/g
    };
    var storyUrl = 'http://floodlightproject.org/stories/so-much-more-than-butterflies/';
    var storyLinkHtml = _.template('<a class="storybase-story-embed" href="{{url}}">So much more than butterflies</a>', {
      url: storyUrl
    });
    var listUrl = 'http://floodlightproject.org/projects/finding-a-bite-food-access-in-the-childrens-corrid/'
    var listLinkHtml = _.template('<a class="storybase-list-embed" href="{{url}}">Finding a Bite: Food Access in the Childrens Corridor</a>', {
      url: listUrl
    });
    var storyWithListHtml = _.template('<div class="storybase-story-list-embed"><a class="storybase-story" href="{{storyUrl}}">Local Grown: Images of the Mo Betta Market</a><a class="storybase-list" href="{{listUrl}}">Finding a Bite: Food Access in the Childrens Corridor</a></div>', {
      storyUrl: storyUrl,
      listUrl: listUrl
    });
    var getWidgetUrl = function(storyUrl, listUrl) {
      var queryParams = [];
      var url = "http://floodlightproject.org/widget/";
      if (storyUrl) {
        queryParams.push('story-url=' + encodeURIComponent(storyUrl));
      }
      if (listUrl) {
        queryParams.push('list-url=' + encodeURIComponent(listUrl));
      }
      if (queryParams.length) {
        url = url + '?' + queryParams.join('&'); 
      }

      return url;
    };
                  
    var $sandbox;
    var $storyLink;
    var $listLink;

    beforeEach(function() {
      $sandbox = $('#sandbox');
      $storyLink = $(storyLinkHtml).appendTo($sandbox);
      $listLink = $(listLinkHtml).appendTo($sandbox);
      $storyWithListEl = $(storyWithListHtml).appendTo($sandbox);
      window.storybase.widgets.showWidgets();
    });

    afterEach(function() {
      $sandbox.empty();
    });

    it("replaces links with a class of 'storybase-story-embed' with an iframe", function() {
      var $widget;
      var widgetUrl = getWidgetUrl(storyUrl);

      console.debug(widgetUrl);
      $widget = $sandbox.find("iframe[src='" + widgetUrl + "']");
      expect($widget.length).toEqual(1);
      expect($storyLink.is(':hidden')).toBeTruthy();
    });

    it("replaces links with a class of 'storybase-list-embed' with an iframe", function() {
      var $widget;
      var widgetUrl = getWidgetUrl(null, listUrl);

      $widget = $sandbox.find("iframe[src='" + widgetUrl + "']");
      expect($widget.length).toEqual(1);
      expect($listLink.is(':hidden')).toBeTruthy();
    });

    it("replaces divs with a class of 'storybase-story-list-embed' with an iframe", function() {
      var $widget;
      var widgetUrl = getWidgetUrl(storyUrl, listUrl);

      $widget = $sandbox.find("iframe[src='" + widgetUrl + "']");
      expect($widget.length).toEqual(1);
      expect($storyWithListEl.is(':hidden')).toBeTruthy();
    });
  });
});
