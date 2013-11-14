var initializeGlobals = function() {
  storybase.API_ROOT = '/api/0.1/';
  storybase.MAP_CENTER = [39.74151, -104.98672];
  storybase.MAP_ZOOM_LEVEL = 11;
  storybase.MAP_POINT_ZOOM_LEVEL = 14; 
};

/**
 * Replacement for Backbone's Model.save() that doesn't call through to
 * Backbone.sync()
 */
var mockSave = function(attributes, options) {
  options = options || {};
  _.each(attributes, function(val, key) {
    this.set(key, val);
  }, this);
  // Assign a mock id to the model so isNew() will
  // return false
  this.id = '8b4ffd98c1404b75bb8d7aeaddea2a4d';
  if (options.success) {
    options.success(this);
  }
  return true;
};

var MockSavingModel = Backbone.Model.extend({
  save: mockSave
});

var MockAsset = Backbone.Model.extend({
  idAttribute: 'asset_id',
  acceptsData: function() { return false; }
});

var MockStoryTemplate = Backbone.Model.extend({
  getStory: function(options) {}
});

var EventBus = _.extend({}, Backbone.Events);

describe('AppView', function() {
  beforeEach(function() {
    initializeGlobals();
    // Binding event handlers to the dispatcher happens in the view's
    // initialize method, so we have to spy on the prototype so the
    // spied method will get bound.
    spyOn(storybase.builder.views.AppView.prototype, 'error');
    this.view = new storybase.builder.views.AppView({
      dispatcher: EventBus,
      showTour: false
    });
  });

  afterEach(function() {
    this.view.close();
  });

  it('calls the error method when it receives the "error" event on the event bus', function() {
    var errMsg = 'An error message';
    EventBus.trigger('error', errMsg);
    expect(this.view.error).toHaveBeenCalledWith(errMsg);
  });

  it('sets a "has-story" class on its element when the user selects a template', function() {
    var template = new MockStoryTemplate();
    EventBus.trigger('select:template', template); 
    expect(this.view.$el.hasClass('has-story')).toBeTruthy();
  });
});

describe('SectionEditView view', function() {
  describe('when initialized with an existing story and section', function () {
    beforeEach(function() {
      var Section = Backbone.Model.extend({
        url: function() {
          return '/api/0.1/stories/357c5885c4e844cb8a4cd4eebe912a1c/sections/dc044f23e93649d6b1bd48625fc301cd/';
        }
      });
      var SectionAssets = Backbone.Collection.extend({
        url: function() {
          return '/api/0.1/stories/357c5885c4e844cb8a4cd4eebe912a1c/sections/dc044f23e93649d6b1bd48625fc301cd/assets/';
        },

        parse: function(response) {
          return response.objects;
        }
      });
      var Story = Backbone.Model.extend({
        assets: new Backbone.Collection(),
        url: function() {
          return '/api/0.1/stories/357c5885c4e844cb8a4cd4eebe912a1c/';
        }
      });
      this.section = new Section({
        id: "dc044f23e93649d6b1bd48625fc301cd",
        layout_template: "<div class=\"section-layout side-by-side\">\n    <div class=\"left\">\n        <div class=\"storybase-container-placeholder\" id=\"left\"></div>\n    </div>\n    <div class=\"right\">\n        <div class=\"storybase-container-placeholder\" id=\"right\"></div>\n    </div>\n</div>\n",
      }); 
      this.section.assets = new SectionAssets();
      this.view = new storybase.builder.views.SectionEditView({
        dispatcher: EventBus,
        model: this.section,
        story: new Story(), 
        templateSource: $('#section-edit-template').html()
      });
    });

    describe('when receiving the "do:add:sectionasset" event', function() {
      beforeEach(function() {
        var container = 'left';
        this.asset = new Backbone.Model({
           id: 'bef53407591f4fd8bd169f9cc02672f9',
           type: 'text',
           body: 'Test text asset body',
           content: 'Test text asset body'
        });
        EventBus.trigger('do:add:sectionasset', this.section, this.asset, container); 
      });

      it('should add the asset to the assets collection', function() {
        expect(this.view.assets.size()).toEqual(1);
        expect(this.view.assets.at(0)).toEqual(this.asset);
      });
    });
  });
});

function implementsWorkflowStep(context) {
  describe("implements a workflow step because it", function() {
    var view;

    beforeEach(function() {
      view = context.view;
    });

    it('has a workflowStep property', function() {
      expect(_.isObject(_.result(view, 'workflowStep'))).toBeTruthy();
    });
  });
}

describe('BuilderView view', function() {
  var context = {}; 

  beforeEach(function() {
    spyOn(storybase.builder.views.BuilderView.prototype, 'setStoryTemplate');
    this.view = context.view = new storybase.builder.views.BuilderView({
      dispatcher: EventBus
    });
  });

  afterEach(function() {
    this.view.close();
  });

  describe('when receiving the select:template signal via the dispatcher', function() {
    beforeEach(function() {
      this.storyTemplate = new MockStoryTemplate({
        "description": "Explain a complex issue simply",
        "story": "/api/0.1/stories/0b2b9e3f38e3422ea3899ee66d1e334b/",
        "tag_line": "it doesn't have to be so complicated",
        "template_id": "5586de9ad3674c7e926ca4f4f04da27b",
        "time_needed": "30 minutes", 
        "title": "Explainer"
      });
    });

    it('calls the setStoryTemplate method', function() {
      EventBus.trigger("select:template", this.storyTemplate);
      expect(this.view.setStoryTemplate).toHaveBeenCalledWith(this.storyTemplate);
    });
  });

  implementsWorkflowStep(context);
});

describe('SectionAssetEditView view', function() {
  beforeEach(function() {
    this.assetTypes = [
      {
        'name': 'image',
        'type': 'image'
      },
      {
        'name': 'text',
        'type': 'text'
      }
    ];
    this.view = new storybase.builder.views.SectionAssetEditView({
       assetTypes: this.assetTypes,
       dispatcher: EventBus,
       story: new Backbone.Model()
    });
  });

  describe('when initializing', function() {
    it('should have a model property', function() {
      expect(this.view.model).toBeDefined();
    });

    it('should have a state of "select"', function() {
      expect(this.view.state.name).toEqual('select');
    });
  });

  describe('with an undefined type property', function() {
    describe('when rendering', function(){
      beforeEach(function() {
        this.view.render();
      });

      it('should provide a list of available asset types', function() {
        expect(this.view.$('.asset-type').length).toEqual(_.size(this.assetTypes));
      });
    });

    describe('when a type link is clicked', function() {
      beforeEach(function() {
        this.view.render();
        var $typeLink = this.view.$('.asset-type').first();
        $typeLink.trigger('click');
        this.selectedType = $typeLink.data('asset-type');
      });

      it("should set the model property", function() {
        expect(this.view.model).toBeDefined();
      });

      it("should set the type attribute of the model", function() {
        expect(this.view.model.get('type')).toEqual(this.selectedType);
      });

      it('should provide a form for selecting an asset', function() {
        expect(this.view.$el).toContain('form');
      });
    });
  });

  describe('with the model type attribute set', function() {
    beforeEach(function() {
      // Set the type property to a type that we don't really care
      // about to test for things that should happen regardless of type
      this.view.setType('faketype');
    });

    describe('when rendering', function(){
      beforeEach(function() {
        this.view.render();
      });

      it('should provide a form for selecting an asset', function() {
        expect(this.view.$el).toContain('form');
      });

      it('should provide a submit button', function() {
        expect(this.view.$el).toContain('input[type="submit"]');
      });

      it('should provide a cancel button', function() {
        expect(this.view.$el).toContain('input[type="reset"]');
      });
    });

    describe('when clicking the cancel button', function() {
      beforeEach(function() {
        this.view.render();
        this.view.$('input[type="reset"]').trigger('click');
      });

      it('should re-render the view with a list of available asset types',
         function() {
           expect(this.view.$('.asset-type').length).toEqual(_.size(this.assetTypes));
         }
      );

      it('should not display a form', function() {
        expect(this.view.$el).not.toContain('form');
      });
    });
  });

  describe('with the model type attribute set to "text"', function() {
    beforeEach(function() {
      this.view.setType('text');
    });

    describe('when rendering', function(){
      beforeEach(function() {
        this.view.render();
      });

      it('should not provide a file and url input', function() {
        expect(this.view.$el).not.toContain('input[name="url"]');
        expect(this.view.$el).not.toContain('input[name="file"]');
      });

      it('should include a textarea', function() {
        expect(this.view.$el).toContain('textarea');
      });
    });

    describe('when entering text and submitting', function() {
      beforeEach(function() {
        this.assetBody = 'Test text content';
        this.server = sinon.fakeServer.create();
        this.fixture = this.fixtures.Assets.postList.text;
        this.fixture.body = this.assetBody;
        this.fixture.content = this.assetBody;
        this.server.respondWith(
          "POST",
          "/api/0.1/assets/",
          this.validResponse(this.fixture)
        );
        this.spy = sinon.spy();
        EventBus.on("do:add:sectionasset", this.spy);
        this.view.render();
        this.view.$('textarea[name="body"]').val(this.assetBody);
        this.view.$('form').submit();
      });

      afterEach(function() {
        this.server.restore();
      });

      it('should set the model property', function() {
        expect(this.view.model).toBeDefined();
        expect(this.view.model.get('body')).toEqual(this.assetBody);
        expect(this.view.model.get('type')).toEqual('text');
      });

      it('should save the model', function() {
        this.server.respond();
        expect(this.view.model.isNew()).toBeFalsy();
      });

      it("should display the model's body", function() {
        this.server.respond();
        expect(this.view.$el.text()).toContain(this.view.model.get('body'));
      });

      it('should send the "do:add:sectionasset" event through the dispatcher', function() {
        this.server.respond();
        expect(this.spy.called).toBeTruthy();
      });
    });
  });

  describe('with the model type attribute set to "image"', function() {
    beforeEach(function() {
      this.view.setType('image');
    });

    describe('when rendering', function(){
      beforeEach(function() {
        this.view.render();
      });

      it('should provide a file and url input', function() {
        expect(this.view.$el).toContain('input[name="url"][type="text"]');
        expect(this.view.$el).toContain('input[name="image"][type="file"]');
      });

      it('should not include a body textarea', function() {
        expect(this.view.$el).not.toContain('textarea[name="body"]');
      });
    });
  });

  describe('with the model property set to an existing text asset', function() {
    beforeEach(function() {
       this.view.model = new MockAsset({
         id: 'bef53407591f4fd8bd169f9cc02672f9',
         type: 'text',
         body: 'Test text asset body',
         content: 'Test text asset body'
       });
       // Mock Story.formFieldVisible
       this.view.model.formFieldVisible = function(name, type) {
         return true;
       };
    });

    describe('when in the "display" state', function() {
      beforeEach(function() {
        this.view.setState('display');
      });

      describe('when rendering', function() {
        beforeEach(function() {
          this.view.render();
        });

        it("should display the model's body", function() {
          expect(this.view.$el.text()).toContain(this.view.model.get('body'));
        });
      });
    });
  });
});

describe('DrawerButtonView', function() {
  beforeEach(function() {
    this.parentView = new Backbone.View();
    this.view = new storybase.builder.views.DrawerButtonView({
      callback: function(evt) {
        return true;
      },
      dispatcher: EventBus,
      parent: this.parentView
    });
  });

  describe('when clicking on the button', function() {
    beforeEach(function() {
      this.spy = sinon.spy();
      EventBus.on('do:toggle:drawer', this.spy);
      this.view.$el.trigger('click');
    });

    it('triggers a "do:toggle:drawer" event with the parent view as an argument', function() {
      expect(this.spy.calledWith(this.parentView)).toBeTruthy();
    });
  });
});

describe('DrawerView', function() {
  beforeEach(function() {
    var MockInDrawerView = Backbone.View.extend({
      initialize: function() {
        this.dispatcher = this.options.dispatcher;
      },

      drawerButton: function() {
        return new storybase.builder.views.DrawerButtonView({
          dispatcher: this.dispatcher,
          buttonId: this.options.testViewId,
          title: this.options.testViewId,
          text: this.options.testViewId,
          callback: function(evt) {
            return true;
          },
          parent: this
        });
      },
      drawerOpenEvents: '',
      drawerCloseEvents: '',
      show: function() {},
      hide: function() {}
    });
    this.inDrawer1 = new MockInDrawerView({
      testViewId: 'test',
    });
    this.inDrawer2 = new MockInDrawerView({
      testViewId: 'test2',
    });
    this.view = new storybase.builder.views.DrawerView({
      dispatcher: EventBus
    });
    this.view.registerView(this.inDrawer1);
    this.view.registerView(this.inDrawer2);
  });

  describe('when closed', function() {
    beforeEach(function() {
      this.view.close();
    });

    describe('and receiving a "do:toggle:drawer" event', function() {
      beforeEach(function() {
        EventBus.trigger('do:toggle:drawer', this.inDrawer1);
      });

      it('should set the drawer state to open', function() {
        expect(this.view.isOpen()).toBeTruthy();
      });

      it('the drawer contents element should be visible', function() {
        var $contentsEl = this.view.$(this.view.options.contentsEl);
        expect($contentsEl.css('display')).toNotEqual('none');
      });

      it('the active view should be the one passed with the event', function() {
        expect(this.view.activeView().cid).toEqual(this.inDrawer1.cid);
      });
    });
  });

  describe('when opened', function() {
    describe('with a view', function() {
      beforeEach(function() {
        this.view.open(this.inDrawer1);
        expect(this.view.isOpen()).toBeTruthy();
        this.activeView = this.view.activeView();
      });

      describe('and receiving a "do:toggle:drawer" event with the active view', function() {
        beforeEach(function() {
          EventBus.trigger('do:toggle:drawer', this.inDrawer1);
        });

        it('should set the drawer state to closed', function() {
          expect(this.view.isOpen()).toBeFalsy();
        });

        it('the drawer contents element should be hidden', function() {
          var $contentsEl = this.view.$(this.view.options.contentsEl);
          expect($contentsEl.css('display')).toEqual('none');
        });

        it('the active view should remain unchanged', function() {
          expect(this.view.activeView().cid).toEqual(this.activeView.cid);
        });
      });

      describe('and receiving a "do:toggle:drawer" event with a different view', function() {
        beforeEach(function() {
          EventBus.trigger('do:toggle:drawer', this.inDrawer2);
        });

        it('the drawer state should remain open', function() {
          expect(this.view.isOpen()).toBeTruthy();
        });

        it('the drawer contents element should be visible', function() {
          var $contentsEl = this.view.$(this.view.options.contentsEl);
          expect($contentsEl.css('display')).toNotEqual('none');
        });

        it('the active view should be the one passed with the event', function() {
          expect(this.view.activeView().cid).toEqual(this.inDrawer2.cid);
        });
      });
    });
  });
});

var MockStory = Backbone.Model.extend({
  initialize: function(attributes, options) {
    this.assets = new Backbone.Collection();
  },

  // Mock story's save method so it doesn't try to do a request,
  save: function(attributes, options) {
    _.each(attributes, function(val, key) {
      this.set(key, val);
    }, this);
    return true;
  },

  // Stub the getFeaturedAsset method.  This can be overridden with
  // spyOn().return() to change the behavior.
  getFeaturedAsset: function() {
    return undefined;
  },

  // Stub the setFeaturedAsset method. This can be overridden with
  // spyOn() to change the behavior.
  setFeaturedAsset: function(asset, options) {},

  setFeaturedAssets: function(collection) {
    this.featuredAssets = collection;
  },
});


describe('PublishButtonView', function() {
  beforeEach(function() {
    this.story = new MockStory();
  });

  describe('when rendered with an unpublished story', function() {
    beforeEach(function() {
      this.story.set('status', 'draft');
      this.view = new storybase.builder.views.PublishButtonView({
        dispatcher: EventBus,
        model: this.story
      });
      this.view.render();
    });

    it("should show a button", function() {
      expect(this.view.$('button').length).toEqual(1);
    });
  });

  describe('when rendered with a published story', function() {
    beforeEach(function() {
      this.story.set('status', 'published');
      this.view = new storybase.builder.views.PublishButtonView({
        dispatcher: EventBus,
        model: this.story
      });
      this.view.render();
    });

    it("should not show a button", function() {
      expect(this.view.$('button').length).toEqual(0);
    });

    describe("and the story's status is set to 'draft'", function() {
      beforeEach(function () {
        this.story.set('status', 'draft');
      });

      it("should show a button", function() {
        expect(this.view.$('button').length).toEqual(1);
      });
    });
  });

  describe('when the user clicks the "Publish" button', function() {
    beforeEach(function() {
      this.story.set('status', 'draft');
      this.view = new storybase.builder.views.PublishButtonView({
        dispatcher: EventBus,
        model: this.story
      });
      spyOn(this.story, 'save').andCallThrough();
      this.view.render();
      this.view.$('button').trigger('click');
    });

    it('should save the story', function() {
      expect(this.story.save).toHaveBeenCalled();
    });

    it('should hide the button', function() {
      expect(this.view.$('button').length).toEqual(0);
    });
  });
});

describe('PublishedButtonsView', function() {
  beforeEach(function() {
    this.story = new MockStory();
    this.view = new storybase.builder.views.PublishedButtonsView({
      model: this.story,
      dispatcher: EventBus
    });
    $('#sandbox').append(this.view.$el);
  });

  afterEach(function() {
    this.view.remove();
  });

  describe("when its story is unpublished", function() {
    beforeEach(function() {
      this.story.set('status', 'draft');
    });

    it('has a hidden rendered element', function() {
      expect(this.view.render().$el.is(':visible')).toBeFalsy();
    });
  });

  describe("when its story is published", function() {
    beforeEach(function() {
      this.story.set('status', 'published');
    });

    it('has a visible rendered element', function() {
      expect(this.view.render().$el.is(':visible')).toBeTruthy();
    });

    it('has a "View" button', function() {
      expect(this.view.render().$('a,button').filter(':contains("View")').length).toEqual(1);
    });

    it('has a "Unpublish" button', function() {
      expect(this.view.render().$('a,button').filter(':contains("Unpublish")').length).toEqual(1);
    });

    describe("clicking on the unpublish button", function() {
      beforeEach(function() {
        this.view.render().$('a,button').filter(':contains("Unpublish")').click();
      });

      it('should set the story status to "draft"', function() {
        expect(this.story.get('status')).toEqual('draft');
      });
    });
  });
});

describe('LegalView', function() {
  beforeEach(function() {
    var MockStory = Backbone.Model.extend({});
    this.story = new MockStory();
    this.view = new storybase.builder.views.LegalView({
      dispatcher: EventBus,
      model: this.story
    });
    $('#sandbox').append(this.view.$el);
  });

  describe('when the story is unpublished', function() {
    beforeEach(function() {
      this.story.set('status', 'draft');
    });

    it('should be visible', function() {
      expect(this.view.$el.is(':visible')).toBeTruthy();
    });
  });

  describe('when the story is published', function() {
    beforeEach(function() {
      this.story.set('status', 'published');
    });

    it('should be hidden', function() {
      expect(this.view.$el.is(':hidden')).toBeTruthy();
    });
  });
});

describe('LicenseView', function() {
  beforeEach(function() {
    this.story = new MockStory();
  });

  describe('when initialized with a model with a CC BY license', function() {
    beforeEach(function() {
      this.story.set('license', 'CC BY');
      this.view = new storybase.builder.views.LicenseView({
        dispatcher: EventBus,
        model: this.story
      });
    });

    afterEach(function() {
      this.view.close();
    });

    describe("and rendered", function() {
      beforeEach(function() {
        this.view.render();
      });

      it("sets the allow commercial radio button to yes", function() {
        expect(this.view.$('[name="cc-allow-commercial"]:checked').val()). toEqual('y');
      });

      it("sets the allow modification radio button to yes", function() {
        expect(this.view.$('[name="cc-allow-modification"]:checked').val()). toEqual('y');
      });
    });

    describe("and the user sets the allow commercial radio button to no and the allow modification radio button to no", function() {
      beforeEach(function() {
        this.view.render();
        this.view.$('[name="cc-allow-commercial"][value="n"]').prop('checked', true).trigger('change');
        this.view.$('[name="cc-allow-modification"][value="n"]').prop('checked', true).trigger('change');
      });

      it("sets the model's license to 'CC BY-NC-ND'", function() {
        expect(this.story.get('license')).toEqual("CC BY-NC-ND");
      });
    });
  });

  describe('when initialized with a model with a Creative Commons Attribution-NonComemrcial-ShareAlike license', function() {
    beforeEach(function() {
      this.licenseVal = 'CC BY-NC-SA';
      this.story.set('license', this.licenseVal);
      this.view = new storybase.builder.views.LicenseView({
        dispatcher: EventBus,
        model: this.story
      });
    });

    afterEach(function() {
      this.view.close();
    });

    describe("and rendered", function() {
      beforeEach(function() {
        this.view.render();
      });

      it("sets the allow commercial radio button to no", function() {
        expect(this.view.$('[name="cc-allow-commercial"]:checked').val()). toEqual('n');
      });

      it("sets the allow modification radio button to share-alike", function() {
        expect(this.view.$('[name="cc-allow-modification"]:checked').val()). toEqual('sa');
      });
    });
  });
});

describe('FeaturedAssetDisplayView', function() {
  beforeEach(function() {
    this.featuredAsset1 = new MockAsset({
        content: '<img class="asset-thumbnail featured-asset" alt="" src="/media/filer_thumbnails/2013/01/02/test_image1.jpg">' 
    });
    this.featuredAsset2 = new MockAsset({
        content: '<img class="asset-thumbnail featured-asset" alt="" src="/media/filer_thumbnails/2013/01/02/test_image2.jpg">' 
    });
    this.story = new MockStory();
    this.defaultImageUrl = '../img/default-image-story-335-200.png';
    this.view = new storybase.builder.views.FeaturedAssetDisplayView({
      dispatcher: EventBus,
      model: this.story,
      defaultImageUrl: this.defaultImageUrl
    });
  });

  describe("when the story doesn't have a featured asset set", function() {
    it("should show the default image", function() {
      expect(this.view.render().$el.html()).toContain(this.defaultImageUrl);
    });

    describe("and a featured image is selected", function() {
      beforeEach(function() {
        expect(this.view.render().$el.html()).toContain(this.defaultImageUrl);
        // Stub Story.getFeaturedAsset
        spyOn(this.story, "getFeaturedAsset").andReturn(this.featuredAsset1);
      });

      it("should show the featured image", function() {
        expect(this.view.render().$el.html()).toNotContain(this.defaultImageUrl);
        expect(this.view.$el.html()).toContain(this.featuredAsset1.get('content'));
      });
    });
  });

  describe("when the story has a featured image set", function() {
    beforeEach(function() {
      // Stub Story.getFeaturedAsset
      spyOn(this.story, "getFeaturedAsset").andReturn(this.featuredAsset1);
    });

    it("should show the featured image", function() {
      expect(this.view.render().$el.html()).toNotContain(this.defaultImageUrl);
      expect(this.view.$el.html()).toContain(this.featuredAsset1.get('content'));
    });
  });

  describe("when the story's featured image changes", function() {
    beforeEach(function() {
      // Stub Story.getFeaturedAsset
      this.gfaStub = spyOn(this.story, "getFeaturedAsset").andReturn(this.featuredAsset1);
      this.story.trigger("set:featuredasset");
    });

    it("should show the new featured image", function() {
      // Expect the old featured asset
      expect(this.view.render().$el.html()).toContain(this.featuredAsset1.get('content'));
      // Mock changing the featured image
      this.gfaStub.andReturn(this.featuredAsset2);
      this.story.trigger("set:featuredasset");
      expect(this.view.render().$el.html()).toContain(this.featuredAsset2.get('content'));
    });
  });
});

describe('FeaturedAssetSelectView', function() {
  beforeEach(function() {
    this.story = new MockStory();
    this.asset1 = new MockAsset({
      asset_id: '0e279cbb85af43d9a9244c9b252edf71',
      type: 'image',
      content: '<img class="asset-thumbnail featured-asset" alt="" src="/media/filer_thumbnails/2013/01/02/test_image1.jpg">', 
      thumbnail_url: '/media/filer_thumbnails/2013/01/02/test_image1__222x222_q85.jpg'
    });
    this.asset2 = new MockAsset({
      asset_id: 'ecbe6e3f515a46259481c1efeb06d0b6',
      type: 'image',
      content: '<img class="asset-thumbnail featured-asset" alt="" src="/media/filer_thumbnails/2013/01/02/test_image2.jpg">', 
      thumbnail_url: '/media/filer_thumbnails/2013/01/02/test_image2__222x222_q85.jpg'
    });
    this.asset3 = new MockAsset({
      asset_id: '8e07570bb73940839026864cdb931501',
      type: 'image',
      content: '<img class="asset-thumbnail featured-asset" alt="" src="/media/filer_thumbnails/2013/01/02/test_image2.jpg">', 
      thumbnail_url: '/media/filer_thumbnails/2013/01/02/test_image3__222x222_q85.jpg'
    });
    // Simulate SectionAssetEditView.addAsset's behavior
    this.simulateAddAsset = function(asset) {
      this.story.assets.add(asset);
      // Simulate saving the assets to the server 
      this.story.assets.trigger('sync');
    };
  });

  describe("when initialized with a story with no image assets", function() {
    beforeEach(function() {
      this.view = new storybase.builder.views.FeaturedAssetSelectView({
        dispatcher: EventBus,
        model: this.story
      });
    });

    it('should show no images when rendered', function() {
      expect(this.view.render().$('img').length).toEqual(0);
    });

    it('should show the images when an asset is added', function() {
      expect(this.view.render().$('img').length).toEqual(0);
      this.simulateAddAsset(this.asset1);
      expect(this.view.$('img').length).toEqual(1);
      expect(this.view.$el.html()).toContain(this.asset1.get('thumbnail_url'));
    });
  });

  describe("when initialized with a story with image assets", function() {
    beforeEach(function() {
      this.story.assets.reset([this.asset1, this.asset2]);
      this.view = new storybase.builder.views.FeaturedAssetSelectView({
        dispatcher: EventBus,
        model: this.story
      });
    });

    it('should show the images when rendered', function() {
      expect(this.view.render().$('img').length).toEqual(2);
      expect(this.view.$el.html()).toContain(this.asset1.get('thumbnail_url'));
      expect(this.view.$el.html()).toContain(this.asset2.get('thumbnail_url'));
    });

    it("it should show new images when they're added", function() {
      this.simulateAddAsset(this.asset3);
      expect(this.view.$el.html()).toContain(this.asset1.get('thumbnail_url'));
      expect(this.view.$el.html()).toContain(this.asset2.get('thumbnail_url'));
      expect(this.view.$el.html()).toContain(this.asset3.get('thumbnail_url'));
    });
  });

  describe("when rendered with a featured asset selected", function() {
    beforeEach(function() {
      this.story.assets.reset([this.asset1, this.asset2]);
      // Stub Story.getFeaturedAsset
      this.gfaStub = spyOn(this.story, "getFeaturedAsset").andReturn(this.asset1);
      this.view = new storybase.builder.views.FeaturedAssetSelectView({
        dispatcher: EventBus,
        model: this.story
      });
    });

    it("should show the featured asset as highlighted when rendered", function() {
      this.view.render();
      expect(this.view.$('.selected').length).toEqual(1);
      expect(this.view.$('.selected').first().html()).toContain(
        this.asset1.get('thumbnail_url'));
    });

    describe("when a new featured asset is selected through another view", function() {
      beforeEach(function() {
        // Mock changing the featured image
        this.story.assets.add(this.asset3);
        this.gfaStub.andReturn(this.asset3);
        this.story.trigger("set:featuredasset");
      });

      it("should show the new featured asset as selected", function() {
        expect(this.view.$('.selected').length).toEqual(1);
        expect(this.view.$('.selected').first().html()).toContain(
          this.asset3.get('thumbnail_url'));
      });
    });  

    describe("when a user clicks a thumbnail to select a featured asset", function() {
      beforeEach(function() {
        this.view.render();
        var spec = this;
        // Stub Story.setFeaturedAsset
        this.sfaStub = spyOn(this.story, "setFeaturedAsset").andCallFake(function(asset, options) {
          spec.gfaStub.andReturn(asset);
          spec.story.trigger("set:featuredasset", asset);
        });
        // Find the element for this.asset2 and click it
        this.sel = "img[src='" + this.asset2.get('thumbnail_url') + "']";
      });

      it("should show the clicked thumbnail as selected", function() {
        this.view.$(this.sel).click();
        expect(this.view.$('.selected').length).toEqual(1);
        expect(this.view.$('.selected').first().html()).toContain(
          this.asset2.get('thumbnail_url'));
      });
    });
  });
});

// NOTE: We only test creating a new featured asset by URL because
// I couldn't think of a clean way to trigger/mock the image
// upload in JavaScript.
describe("FeaturedAssetAddView", function() {
   beforeEach(function() {
     this.story = new MockStory();
     // Stub the saving of the asset.  In a perfect world, we'd
     // mock the entire class, but we'd have to repeat the 
     // implementation of the schema method.
     var MockSavingAsset = storybase.models.Asset.extend({
       save: mockSave
     });
     this.view = new storybase.builder.views.FeaturedAssetAddView({
       dispatcher: EventBus,
       model: this.story,
       defaultImageUrl: this.defaultImageUrl,
       assetModelClass: MockSavingAsset
     });
   });

   describe("when rendered", function() {
     beforeEach(function() {
       this.view.render();
     });
     
     it("should show an input for a URL", function() {
       expect(this.view.$('input[type=text][name=url]').length).toEqual(1);
     });

     it("should show an input for a file", function() {
       expect(this.view.$('input[type=file]').length).toEqual(1);
     });

     it("should show a submit button", function() {
       expect(this.view.$('[type=submit]').length).toEqual(1);
     });

     it("should show a reset button", function() {
       expect(this.view.$('[type=reset]').length).toEqual(1);
     });
   });

   describe("when the user specifies a URL", function() {
     beforeEach(function() {
       this.url = 'http://www.flickr.com/photos/79208145@N08/7803936842/';
       this.sfaStub = spyOn(this.story, "setFeaturedAsset");
       this.view.render();
     });

     it("should set the featured asset on the story when the form is submitted", function() {
       this.view.$('[name=url]').val(this.url);
       this.view.$('form').submit();
       expect(this.sfaStub).toHaveBeenCalled();
     });
   });
});

describe("FeaturedAssetView", function() {
   beforeEach(function() {
     // Mock the subviews. We're not testing them.
     this.MockFeaturedAssetAddView = Backbone.View.extend({
       id: 'featured-asset-add',
       options: {
         title: "Current image"
       },
       enabled: true
     });
     this.MockFeaturedAssetDisplayView = Backbone.View.extend({
       id: 'featured-asset-display',
       options: {
         title: "Add a new image"
       },
       enabled: true
     });
     this.MockFeaturedAssetSelectView = Backbone.View.extend({
       id: 'featured-asset-select',
       options: {
         title: "Select an image from the story"
       },
       enabled: false
     });
     this.getNavItem = function(view) {
       return this.view.$('[href=#' + view.id + ']'); 
     };
     this.story = new MockStory();
     this.story.featuredAssets = new Backbone.Collection();
     this.view = new storybase.builder.views.FeaturedAssetView({
       model: this.story,
       addViewClass: this.MockFeaturedAssetAddView,
       displayViewClass: this.MockFeaturedAssetDisplayView,
       selectViewClass: this.MockFeaturedAssetSelectView,
       dispatcher: EventBus
     });
     // Append the view's element to the DOM so we can test
     // for visibility
     $('#sandbox').append(this.view.$el);

   });

   describe("when initialized with a story with image assets but no featured image", function() {
     beforeEach(function() {
       this.imgAsset = new MockAsset({
         type: 'image'
       });
       this.textAsset = new MockAsset({
         type: 'text'
       });
       this.story.assets.add(this.imgAsset);
       this.story.assets.add(this.textAsset);
       spyOn(this.story, 'setFeaturedAsset');
       this.view = new storybase.builder.views.FeaturedAssetView({
         model: this.story,
         addViewClass: this.MockFeaturedAssetAddView,
         displayViewClass: this.MockFeaturedAssetDisplayView,
         selectViewClass: this.MockFeaturedAssetSelectView,
         dispatcher: EventBus
       });
     });

     it("should set the featured image to an image asset in the story's assets", function() {
       expect(this.story.setFeaturedAsset).toHaveBeenCalledWith(this.imgAsset);
     });
   });

   describe("when initialized with a story with no image assets", function() {
     beforeEach(function() {
       var spec = this;
       this.imgAsset = new MockAsset({
         type: 'image'
       });
       this.imgAsset2 = new MockAsset({
         type: 'image'
       });
       spyOn(this.story, 'setFeaturedAsset').andCallFake(function(asset, options) {
          spec.story.trigger("set:featuredasset", asset);
       });
       // Simulate adding and image and retrieving the synced values from the
       // server
       this.mockImageAdd = function(asset) {
         spec.story.assets.add(asset);
         asset.set('content', '<img class="asset-thumbnail featured-asset" alt="" src="/media/filer_thumbnails/2013/01/02/test_image1.jpg">');
       };
     });

     it("should set the featured asset when an image asset is added to the story", function() {
       this.mockImageAdd(this.imgAsset); 
       expect(this.story.setFeaturedAsset).toHaveBeenCalledWith(this.imgAsset);
     });

     it("should not set the featured asset when a second image asset is added to the story", function() {
       this.mockImageAdd(this.imgAsset); 
       expect(this.story.setFeaturedAsset).toHaveBeenCalledWith(this.imgAsset);
       this.mockImageAdd(this.imgAsset2); 
       expect(this.story.setFeaturedAsset).wasNotCalledWith(this.imgAsset2);
     });
   });

   describe("when initially rendered", function() {
     beforeEach(function() {
       this.view.render();
     });

     it("should show the display subview and hide the other subviews", function() {
       expect(this.view.displayView.$el.is(':hidden')).toBeFalsy();
       expect(this.view.addView.$el.is(':hidden')).toBeTruthy();
       expect(this.view.selectView.$el.is(':hidden')).toBeTruthy();
     });

     it("should show a navigation element", function() {
       expect(this.view.$('.nav').length).toEqual(1);
     });

     it("should show only the display view's navigation item as active", function() {
       expect(this.getNavItem(this.view.displayView).parent().hasClass('active')).toBeTruthy(); 
       expect(this.getNavItem(this.view.addView).parent().hasClass('active')).toBeFalsy(); 
       expect(this.getNavItem(this.view.selectView).parent().hasClass('active')).toBeFalsy(); 
     });
   });

  describe("when the add view's navigation item is clicked", function() {
    beforeEach(function() {
      this.view.render();
      this.getNavItem(this.view.addView).click();
    });

    it("should show the add subview and hide the other subviews", function() {
      expect(this.view.displayView.$el.is(':hidden')).toBeTruthy();
      expect(this.view.addView.$el.is(':hidden')).toBeFalsy();
      expect(this.view.selectView.$el.is(':hidden')).toBeTruthy();
    });

    it("should show only the add subview's navigation item as active", function() {
       expect(this.getNavItem(this.view.displayView).parent().hasClass('active')).toBeFalsy(); 
       expect(this.getNavItem(this.view.addView).parent().hasClass('active')).toBeTruthy(); 
       expect(this.getNavItem(this.view.selectView).parent().hasClass('active')).toBeFalsy(); 
    });

    describe("when a featured image is selected", function() {
      beforeEach(function() {
        this.story.trigger("set:featuredasset");
      });

      it("should switch back to showing the display subview", function() {
       expect(this.view.displayView.$el.is(':hidden')).toBeFalsy();
       expect(this.view.addView.$el.is(':hidden')).toBeTruthy();
       expect(this.view.selectView.$el.is(':hidden')).toBeTruthy();
       expect(this.getNavItem(this.view.displayView).parent().hasClass('active')).toBeTruthy(); 
       expect(this.getNavItem(this.view.addView).parent().hasClass('active')).toBeFalsy(); 
       expect(this.getNavItem(this.view.selectView).parent().hasClass('active')).toBeFalsy(); 
      });
    });
  });

  describe("when the select subview is disabled", function() {
     beforeEach(function() {
       this.view.selectView.enabled = false;
       this.view.render();
     });
    it("should show the select subview's nav item as disabled", function() {
       expect(this.getNavItem(this.view.selectView).parent().hasClass('disabled')).toBeTruthy(); 
    });

    it("should not change the the displayed view when the select subview's navigation item is clicked", function() {
       this.getNavItem(this.view.selectView).click();
       expect(this.getNavItem(this.view.selectView).parent().hasClass('active')).toBeFalsy(); 
       expect(this.view.selectView.$el.is(':hidden')).toBeTruthy();
    });

    describe("when an asset is added to the story", function() {
      beforeEach(function() {
        var asset = new MockAsset(); 
        this.view.selectView.enabled = true;
        this.story.assets.add(asset);
      });

      it("should enable the navigation item for the select subview", function() {
        expect(this.getNavItem(this.view.selectView).parent().hasClass('disabled')).toBeFalsy();
      });
    });  
  });  
});

function getHeader(title, byline) {
    title = title || "Test Title";
    byline = byline || "Test Byline";
    var html = '<div class="title-container">' +
      '<a class="logo"><img src="builder-logo.png" /></a>' +
      '<h1 class="title">' + title + '</h1>'+
      '<div class="byline-container"><span class="byline">' + byline + '</span></div>' +
      '</div>';
    return $(html);
}

describe('TitleView', function() {
  beforeEach(function() {
    var spec = this;
    this.title = "Near Northeast Profile: Interactive Slideshow"; 
    // Selectors, relative to the view's element for interface elements of
    // interest.  Make these variables so the tests are less brittle if
    // we change the markup.
    // 
    // Input for editing the title
    this.$el = getHeader(this.title).appendTo($('#sandbox'));
    // Element that contains the title text for display
    this.$title = this.$el.find('.title');
    this.$editor = function() {
      return this.$el.find('input[name="title"]');
    };
    this.story = new MockSavingModel({
      title: this.title
    });
    sinon.spy(this.story, 'save');
    this.view = new storybase.builder.views.TitleView({
      el: this.$el,
      model: this.story,
      dispatcher: EventBus
    });
    sinon.spy(this.view, 'render');

    this.initialSaveCallback = sinon.spy(function() {
      this.view.model.save();  
    });
    EventBus.on('do:save:story', this.initialSaveCallback, this);

    this.editTitle = _.bind(function(newTitle) {
      this.$title.trigger('click');
      this.$editor().val(newTitle);
    }, this);

    this.addMatchers({
      toHaveTitle: function(expected) {
        var view = this.actual;
        var $title = spec.$title; 
        var $input = spec.$editor();
        var title = view.model.get('title');

        // The view's model's title should have the expected value       
        if (title != expected) {
          this.message = function() {
            return 'Expected the view\'s model to have the title "' + expected + ' instead it has "' + title + '"';
          };
          return false;
        }

        // The input should be hidden
        if ($input.is(':visible')) {
          this.message = function() {
            return 'Expected the input to be hidden';
          };
          return false;
        }

        // The title element should be visible
        if (!$title.is(':visible')) {
          this.message = function() {
            return 'Expected the title to be visible';
          };
          return false;
        }

        // The expected title text should be shown in the title element
        if ($title.html() != expected) {
          this.message = function() {
            return 'Expected the displayed title to be "' + expected + '"';
          };
          return false;
        }

        // The expected title text should be in the input element
        if ($input.val() != expected) {
          this.message = function() {
            return 'Expected the value of the input to be "' + expected + '"';
          };
          return false;
        }

        return true;
      }
    });
  });

  afterEach(function() {
    this.$el.remove();
    this.story.save.restore();
    this.view.render.restore();

    EventBus.off('do:save:story');
  });

  it('renders the same element it was initialized with', function() {
    expect(this.view.render().$el).toEqual(this.$el);
  });

  it("Updates the display when the model's title is changed", function() {
    var newTitle = "New Title";
    this.story.set('title', newTitle);
    expect(this.view.$el.html()).toContain(newTitle);
  });

  it('adds a tooltip that says "Click to edit title" to its element', function() {
    this.view.render();
    expect(this.$title.attr('title')).toEqual("Click to edit title");
  });

  it('displays the title as "Untitled Story" when the model\'s title is empty', function() {
    this.story.set('title', '');
    expect(this.view.$el.html()).toContain("Untitled Story");
  });

  it('has an empty text input value when the model\'s title is empty', function() {
    this.view.render();
    this.story.set('title', '');
    expect(this.$editor().val()).toEqual('');
  });

  it('shows a text input and sets focus to the input when clicked', function() {
    this.view.render();
    this.$title.trigger('click');
    expect(this.$editor().length).toEqual(1);
    // The title text should be hidden
    expect(this.$title.is(':visible')).toBeFalsy();
    expect(this.$editor().is(':focus')).toBeTruthy();
  });

  it('fires an "edit" event when the title is clicked', function() {
    var spy = sinon.spy();
    this.view.once('edit', spy);
    this.$title.trigger('click');
    expect(spy.called).toBeTruthy();
  });

  it('updates the model and hides the text editor when the text input loses focus', function() {
    var newTitle = "New Title";

    this.view.render();
    this.editTitle(newTitle);
    this.$editor().trigger('blur');
    expect(this.view).toHaveTitle(newTitle);
  });

  it('fires a "display" event when the text input loses focus', function() {
    var spy = sinon.spy();
   
    this.view.render();
    this.editTitle("New Title");
    this.view.once('display', spy);
    this.$editor().trigger('blur');
    expect(spy.called).toBeTruthy();
  });

  it('updates the model and hides the text editor when Enter is pressed inside the text input', function() {
    var newTitle = "New Title";
    var evt = $.Event('keyup');
    evt.which = 13; // Enter

    this.view.render();
    this.editTitle(newTitle);
    this.$editor().trigger(evt);
    expect(this.view).toHaveTitle(newTitle);
  });

  it('hides the text editor when Enter is pressed inside the text input even if the value is unchanged', function() {
    var sameTitle = this.story.get('title');
    var evt = $.Event('keyup');
    evt.which = 13; // Enter

    this.view.render();
    this.editTitle(sameTitle);
    this.$editor().trigger(evt);

    expect(this.view).toHaveTitle(sameTitle);
  });

  it('triggers a "do:save:story" event on the event bus when the story is initially saved', function() {
    // Mock event handler for 'do:save:story'
    var evt = $.Event('keyup');
    evt.which = 13; // Enter

    this.view.render();
    this.editTitle("Initial Title");
    this.$editor().trigger(evt);
    // 'do:save:story' should be triggered once
    expect(this.initialSaveCallback.callCount).toEqual(1);

    this.editTitle("New Title");
    this.$editor().trigger(evt);
    // 'do:save:story' should not be triggered again
    expect(this.initialSaveCallback.callCount).toEqual(1);
  });

  it('saves the model when the title attribute changes', function() {
    this.view.model.set('title', "New Title");
    expect(this.view.model.save.called).toBeTruthy();
  });

  it('renders the view when the model is set', function() {
    this.view.setModel(this.story);
    expect(this.view.render.called).toBeTruthy();
  });

  it('cancels editing and hides the input when Esc is pressed', function() {
    var newTitle = "New Title";
    var oldTitle = this.story.get('title');
    var evt = $.Event('keyup');
    evt.which = 27; // Esc

    this.view.render();
    this.editTitle(newTitle);
    this.$editor().trigger(evt);
    expect(this.view).toHaveTitle(oldTitle);
    expect(this.story.save.called).toBeFalsy();
  });

  it('toggles display of the title when the toggle() method is called', function() {
    this.view.render();
    expect(this.$title.is(':visible')).toBeTruthy();
    this.view.toggle();
    expect(this.$title.is(':visible')).toBeFalsy();
    this.view.toggle();
    expect(this.$title.is(':visible')).toBeTruthy();
  });
});

describe('LogoView', function() {
  beforeEach(function() {
    this.$header = getHeader().appendTo($('#sandbox'));
    // Input for logo
    this.logoSel = '.logo img';
    this.view = new storybase.builder.views.LogoView({
      el: this.$header.find(this.logoSel),
      dispatcher: EventBus
    });
  });

  afterEach(function() {
    this.$header.remove();
  });

  it('updates the image filename when the user selects a template', function() {
    var logoFilename = this.view.options.logoFilename;
    var noStoryLogoFilename = this.view.options.noStoryLogoFilename;
    // The logoFilename option should be defined
    expect(logoFilename).toBeTruthy();
    // The nologoFilename option should be defined
    expect(noStoryLogoFilename).toBeTruthy();

    expect(this.view.$el.attr("src")).toContain(noStoryLogoFilename);
    EventBus.trigger('select:template', {});
    expect(this.view.$el.attr("src")).toContain(logoFilename);
    expect(this.view.$el.attr("src")).not.toContain(noStoryLogoFilename);
  });
});

describe('BylineView', function() {
  beforeEach(function() {
    this.byline = "Ida Tarbell";
    this.$header = getHeader("Test Title", this.byline).appendTo($('#sandbox'));
    this.$el = this.$header.find('.byline-container');
    this.$byline = this.$header.find('.byline');
    this.$editor = function() {
      return this.$header.find('input[name="byline"]');
    };
    this.story = new MockSavingModel({
      title: this.title
    });
    this.view = new storybase.builder.views.BylineView({
      el: this.$el,
      model: this.story,
      dispatcher: EventBus
    });
  });

  afterEach(function() {
    this.$header.remove();
  });

  it("Updates the display when the model's byline is changed", function() {
    var newByline = "Ida B. Tarbell";
    this.story.set('byline', newByline);
    expect(this.view.$el.html()).toContain(newByline);
  });

  it('adds a tooltip that says "Click to edit byline" to its element', function() {
    this.view.render();
    expect(this.$byline.attr('title')).toEqual("Click to edit byline");
  });

  it('displays the title as "Unknown Author" when the model\'s byline is empty', function() {
    this.story.set('byline', '');
    expect(this.view.$el.html()).toContain("Unknown Author");
  });

  it('has an empty text input value when the model\'s title is empty', function() {
    this.view.render();
    this.story.set('byline', '');
    expect(this.$editor().val()).toEqual('');
  });

  it('shows a text input and sets focus to the input when clicked', function() {
    this.view.render();
    this.$byline.trigger('click');
    expect(this.$editor().length).toEqual(1);
    // The title text should be hidden
    expect(this.$byline.is(':visible')).toBeFalsy();
    expect(this.$editor().is(':focus')).toBeTruthy();
  });
});

describe('TaxonomyView', function() {
  var context = {};

  beforeEach(function() {
    storybase.MAP_CENTER = [39.74151, -104.98672];
    storybase.MAP_ZOOM_LEVEL = 11;
    storybase.MAP_POINT_ZOOM_LEVEL = 14;

    this.view = context.view = new storybase.builder.views.TaxonomyView({
      dispatcher: EventBus
    });
  });

  implementsWorkflowStep(context);
});

describe('PublishView', function() {
  var context = {};

  beforeEach(function() {
    this.view = context.view = new storybase.builder.views.PublishView({
      dispatcher: EventBus
    });
  });

  afterEach(function() {
    this.view.close();
  });

  implementsWorkflowStep(context);
});

var workflowStepItems = [
  {
    id: 'build',
    title: "Construct your story using text, photos, videos, data visualizations, and other materials",
    nextTitle: "Write Your Story",
    prevTitle: "Continue Writing Story",
    text: "Build",
    visible: true,
    selected: false,
    path: ''
  },
  {
    id: 'tag',
    title: "Label your story with topics and places so that people can easily discover it on Floodlight",
    text: "Tag",
    visible: true,
    enabled: true, 
    path: 'tag/'
  },
  {
    id: 'publish',
    title: "Post your story to Floodlight and your social networks",
    text: "Publish/Share",
    visible: true,
    enabled: true, 
    path: 'publish/'
  }
];

describe('WorkflowStepView', function() {
  beforeEach(function() {
    storybase.builder.APP_ROOT = '/build/';

    this.view = new storybase.builder.views.WorkflowStepView({
      dispatcher: EventBus,
      items: workflowStepItems 
    });
  });

  it('displays a link for each of the items when rendered', function() {
     var item, $itemLinks, $itemLink;

     this.view.render();
     $itemLinks = this.view.$('li a');

     expect($itemLinks.length).toEqual(workflowStepItems.length);

     for (var i = 0; i < workflowStepItems.length; i++) {
       item = workflowStepItems[i];
       $itemLink = $itemLinks.eq(i);
       expect($itemLink.html()).toEqual(item.text);
       expect($itemLink.attr('href')).toEqual(storybase.builder.APP_ROOT + item.path);
     }
  });
});

describe('WorkflowNextPrevView', function() {
  var WorkflowNextPrevView = storybase.builder.views.WorkflowNextPrevView;

  beforeEach(function() {
    sinon.spy(WorkflowNextPrevView.prototype, 'render');
    this.story = new MockStory();
    this.view = new storybase.builder.views.WorkflowNextPrevView({
      items: workflowStepItems,
      dispatcher: EventBus
    });

    this.addMatchers({
      toHaveVisibleItems: function(count) {
        var notText = this.isNot ? " not" : "";
        var $items = this.actual.$('a');

        if (_.isUndefined(count) && $items.length === 0) {
          this.message = function() {
            return "Expected the view to" + notText + " display items";
          };

          return false;
        }
        else if (!_.isUndefined(count) && $items.length !== count) {
          this.message = function() {
            return "Expected the view to" + notText + " display " + count + " items, instead it displayed " + $items.length;
          };

          return false;
        }

        return true;
      },

      toHavePrevLink: function() {
        var notText = this.isNot ? " not" : "";

        if (this.actual.$('a.prev').length !== 1) {
          this.message = function() {
            return "Expected the view to" + notText + " display a link to the previous workflow step";
          };

          return false;
        }

       return true;
      },

      toHaveNextLink: function() {
        var notText = this.isNot ? " not" : "";

        if (this.actual.$('a.next').length !== 1) {
          this.message = function() {
            return "Expected the view to" + notText + " display a link to the next workflow step";
          };

          return false;
        }

        return true;
      },

      toHavePrevLinkTo: function(stepId) {
        var $link = this.actual.$('a.prev');
        var notText = this.isNot ? " not" : "";

        this.message = function() {
          return "Expected the view to" + notText + " display a link to the previous workflow step \"" + stepId + "\"";
        };

        if ($link.length !== 1) {
          return false;
        }

        if (stepId === 'build' && !$link.attr('href').length) {
          return false;
        }
        else if (stepId !== 'build' && $link.attr('href').indexOf(stepId) === -1) {
          return false;
        }

        return true;
      },

      toHaveNextLinkTo: function(stepId) {
        var $link = this.actual.$('a.next');
        var notText = this.isNot ? " not" : "";

        this.message = function() {
          return "Expected the view to" + notText + " display a link to the next workflow step \"" + stepId + "\"";
        };

        if ($link.length !== 1) {
          return false;
        }

        if (stepId === 'build' && !$link.attr('href').length) {
          return false;
        }
        else if (stepId !== 'build' && $link.attr('href').indexOf(stepId) === -1) {
          return false;
        }

        return true;
      }
    });
  });

  afterEach(function() {
    WorkflowNextPrevView.prototype.render.restore();
  });

  it('has its items property set to the items passed to the constructor', function() {
     var srcItem, dstItem;

     expect(this.view.items.length).toEqual(workflowStepItems.length);
     for (var i = 0; i < workflowStepItems.length; i++) {
       srcItem = workflowStepItems[i];
       dstItem = this.view.items[i];
       expect(dstItem.id).toEqual(srcItem.id);
     }
  });

  it("doesn't display any items when rendered without a model being set", function() {
    this.view.render();
    expect(this.view).not.toHaveVisibleItems();
  });

  it("renders when it is notified that the story has been initialized", function() {
    expect(this.view.render.called).toBeFalsy();
    EventBus.trigger('ready:story', this.story);
    expect(this.view.render.called).toBeTruthy();
  });

  it("doesn't display any items when rendered when no workflow step is active", function() {
    this.view.setStory(this.story);
    expect(this.view).not.toHaveVisibleItems();
  });

  describe("when the first workflow step is active", function() {
    beforeEach(function() {
      this.view.setStory(this.story);
      EventBus.trigger('select:workflowstep', workflowStepItems[0].id);
    });

    it("displays a single link", function() {
      expect(this.view).toHaveVisibleItems(1);
    });

    it("displays no link to the previous step", function() {
      expect(this.view).not.toHavePrevLink();
    });

    it("displays a link to the next step", function() {
      expect(this.view).toHaveNextLinkTo(workflowStepItems[1].id); 
    });
  });

  describe('when the second workflow step is active', function() {
    beforeEach(function() {
      this.view.setStory(this.story);
      EventBus.trigger('select:workflowstep', workflowStepItems[1].id);
    });

    it("displays two links", function() {
      expect(this.view).toHaveVisibleItems(2);
    });

    it('displays a link to the previous step', function() {
      expect(this.view).toHavePrevLinkTo(workflowStepItems[0].id); 
    });

    it('displays a link to the next step', function() {
      expect(this.view).toHaveNextLinkTo(workflowStepItems[2].id); 
    });
  });

  describe('when the last workflow step is active', function() {
    var lastIndex = workflowStepItems.length - 1;

    beforeEach(function() {
      this.view.setStory(this.story);
      EventBus.trigger('select:workflowstep', workflowStepItems[lastIndex].id);
    });

    it("displays a single link", function() {
      expect(this.view).toHaveVisibleItems(1);
    });

    it('displays a link to the previous step', function() {
      expect(this.view).toHavePrevLinkTo(workflowStepItems[lastIndex - 1].id); 
    });

    it('displays no link to the next step', function() {
      expect(this.view).not.toHaveNextLink(); 
    });
  });
});
