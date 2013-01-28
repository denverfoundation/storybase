var initializeGlobals = function() {
  storybase.globals.API_ROOT = '/api/0.1/';
  storybase.globals.MAP_CENTER = [39.74151, -104.98672];
  storybase.globals.MAP_ZOOM_LEVEL = 11;
  storybase.globals.MAP_POINT_ZOOM_LEVEL = 14; 
};

describe('AppView', function() {
  beforeEach(function() {
    initializeGlobals();
    this.dispatcher = _.clone(Backbone.Events);
    this.view = new storybase.builder.views.AppView({
      dispatcher: this.dispatcher
    });
  });

  describe('when receiving the "error" event', function() {
    beforeEach(function() {
      // Binding event handlers to the dispatcher happens in the view's
      // initialize method, so we have to spy on the prototype so the
      // spied method will get bound.
      spyOn(storybase.builder.views.AppView.prototype, 'error');
      this.view = new storybase.builder.views.AppView({
        dispatcher: this.dispatcher
      });
    });

    it('calls the error method', function() {
      var errMsg = 'An error message';
      this.dispatcher.trigger('error', errMsg);
      expect(this.view.error).toHaveBeenCalledWith(errMsg);
    });
  });
});

describe('SectionEditView view', function() {
  beforeEach(function() {
    this.dispatcher = _.clone(Backbone.Events);
  });

  describe('when initialized with an existing story and section', function () {
    beforeEach(function() {
      var Section = Backbone.Model.extend({
        url: function() {
          return '/api/0.1/stories/357c5885c4e844cb8a4cd4eebe912a1c/sections/dc044f23e93649d6b1bd48625fc301cd/'
        }
      });
      var SectionAssets = Backbone.Collection.extend({
        url: function() {
          return '/api/0.1/stories/357c5885c4e844cb8a4cd4eebe912a1c/sections/dc044f23e93649d6b1bd48625fc301cd/assets/'
        },

        parse: function(response) {
          return response.objects;
        }
      });
      var Story = Backbone.Model.extend({
        assets: new Backbone.Collection,
        url: function() {
          return '/api/0.1/stories/357c5885c4e844cb8a4cd4eebe912a1c/';
        }
      });
      this.section = new Section({
        id: "dc044f23e93649d6b1bd48625fc301cd",
        layout_template: "<div class=\"section-layout side-by-side\">\n    <div class=\"left\">\n        <div class=\"storybase-container-placeholder\" id=\"left\"></div>\n    </div>\n    <div class=\"right\">\n        <div class=\"storybase-container-placeholder\" id=\"right\"></div>\n    </div>\n</div>\n",
      }); 
      this.section.assets = new SectionAssets;
      this.view = new storybase.builder.views.SectionEditView({
        dispatcher: this.dispatcher,
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
        this.dispatcher.trigger('do:add:sectionasset', this.section, this.asset, container); 
      });

      it('should add the asset to the assets collection', function() {
        expect(this.view.assets.size()).toEqual(1);
        expect(this.view.assets.at(0)).toEqual(this.asset);
      });
    });
  });
});

describe('BuilderView view', function() {
  beforeEach(function() {
    this.dispatcher = _.clone(Backbone.Events);
    this.view = new storybase.builder.views.BuilderView({
      dispatcher: this.dispatcher
    });
  });

  describe('when receiving the select:storytemplate signal via the dispatcher', function() {
    beforeEach(function() {
      // Mock a story template
      var StoryTemplate = Backbone.Model.extend({
        getStory: function(options) {
        }
      });
      this.storyTemplate = new StoryTemplate({
        "description": "Explain a complex issue simply",
        "story": "/api/0.1/stories/0b2b9e3f38e3422ea3899ee66d1e334b/",
        "tag_line": "it doesn't have to be so complicated",
        "template_id": "5586de9ad3674c7e926ca4f4f04da27b",
        "time_needed": "30 minutes", 
        "title": "Explainer"
      });
      spyOn(storybase.builder.views.BuilderView.prototype, 'setStoryTemplate');
      this.view = new storybase.builder.views.BuilderView({
        dispatcher: this.dispatcher
      });
    });

    it('calls the setStoryTemplate method', function() {
      this.dispatcher.trigger("select:template", this.storyTemplate);
      expect(this.view.setStoryTemplate).toHaveBeenCalledWith(this.storyTemplate);
    });
  });
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
    this.dispatcher = _.clone(Backbone.Events);
    this.view = new storybase.builder.views.SectionAssetEditView({
       assetTypes: this.assetTypes,
       dispatcher: this.dispatcher,
       story: new Backbone.Model
    });
  });

  describe('when initializing', function() {
    it('should have a model property', function() {
      expect(this.view.model).toBeDefined();
    });

    it('should have a form property', function() {
      expect(this.view.form).toBeDefined();
    });

    it('should have a state of "select"', function() {
      expect(this.view.getState()).toEqual('select');
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
        this.dispatcher.on("do:add:sectionasset", this.spy);
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

      it('should not include a textarea', function() {
        expect(this.view.$el).not.toContain('textarea');
      });
    });
  });

  describe('with the model property set to an existing text asset', function() {
    beforeEach(function() {
       this.view.model = new Backbone.Model({
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
    this.dispatcher = _.clone(Backbone.Events);
    this.parentView = new Backbone.View;
    this.view = new storybase.builder.views.DrawerButtonView({
      callback: function(evt) {
        return true;
      },
      dispatcher: this.dispatcher,
      parent: this.parentView
    });
  });

  describe('when clicking on the button', function() {
    beforeEach(function() {
      this.spy = sinon.spy();
      this.dispatcher.on('do:toggle:drawer', this.spy);
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
    this.dispatcher = _.clone(Backbone.Events);
    this.inDrawer1 = new MockInDrawerView({
      testViewId: 'test',
    });
    this.inDrawer2 = new MockInDrawerView({
      testViewId: 'test2',
    });
    this.view = new storybase.builder.views.DrawerView({
      dispatcher: this.dispatcher
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
        this.dispatcher.trigger('do:toggle:drawer', this.inDrawer1);
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
          this.dispatcher.trigger('do:toggle:drawer', this.inDrawer1);
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
          this.dispatcher.trigger('do:toggle:drawer', this.inDrawer2);
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
  // Mock story's save method so it doesn't try to do a request,
  save: function(attributes, options) {
    _.each(attributes, function(val, key) {
      this.set(key, val);
    }, this);
    return true;
  }
});

describe('PublishButtonView', function() {
  beforeEach(function() {
    var MockTodoView = Backbone.View.extend({
      ready: function() {
        return false;
      }
    });
    this.todoView = new MockTodoView();
    this.story = new MockStory();
    this.dispatcher = _.clone(Backbone.Events);
  });

  describe('when rendered with an unpublished story', function() {
    beforeEach(function() {
      this.story.set('status', 'draft');
      this.view = new storybase.builder.views.PublishButtonView({
        dispatcher: this.dispatcher,
        model: this.story,
        todoView: this.todoView
      });
      this.view.render();
    });

    it("should show a button", function() {
      expect(this.view.$('button').length).toEqual(1);
    });

    describe("and the story is ready to be published", function() {
      beforeEach(function() {
        this.todoView.ready = function() {
          return true;
        }
        this.view.render();
      });

      it("should make the button enabled", function() {
        expect(this.view.$('button').length).toEqual(1);
        expect(this.view.$('button').filter(':disabled').length).toEqual(0);
      });

      describe('and it receives the "notreadytopublish:story" event', function() {
        beforeEach(function() {
          this.dispatcher.trigger("notreadytopublish:story");
        });

        it("should show the button disabled", function() {
          expect(this.view.$('button').filter(':disabled').length).toEqual(1);
        });
      });
    });

    describe("and the story is not ready to be published", function() {
      beforeEach(function() {
        this.todoView.ready = function() {
          return false;
        }
        this.view.render();
      });

      it("should show the button disabled", function() {
        expect(this.view.$('button').filter(':disabled').length).toEqual(1);
      });

      describe('and it receives the "readytopublish:story" event', function() {
        beforeEach(function() {
          this.dispatcher.trigger("readytopublish:story");
        });

        it("should show the button enabled", function() {
          expect(this.view.$('button').length).toEqual(1);
          expect(this.view.$('button').filter(':disabled').length).toEqual(0);
        });
      });
    });
  });

  describe('when rendered with a published story', function() {
    beforeEach(function() {
      this.story.set('status', 'published');
      this.view = new storybase.builder.views.PublishButtonView({
        dispatcher: this.dispatcher,
        model: this.story,
        todoView: this.todoView
      });
      this.view.render();
    });

    it("should not show a button", function() {
      expect(this.view.$('button').length).toEqual(0);
    });

    describe("and it receives the 'unpublish:story' signal", function() {
      beforeEach(function () {
        this.story.set('status', 'draft');
        this.dispatcher.trigger('unpublish:story');
      });

      it("should show a button", function() {
        expect(this.view.$('button').length).toEqual(1);
      });
    });
  });

  describe('when the user clicks the "Publish" button', function() {
    beforeEach(function() {
      this.story.set('status', 'draft');
      this.todoView.ready = function() {
        return true;
      };
      this.view = new storybase.builder.views.PublishButtonView({
        dispatcher: this.dispatcher,
        model: this.story,
        todoView: this.todoView
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

describe('PublishTodoView', function() {
  beforeEach(function() {
    this.MockCompletedView = Backbone.View.extend({
      completed: function() {
        return true;
      }
    });
    this.MockNotCompletedView = Backbone.View.extend({
      completed: function() {
        return false;
      }
    });
    this.story = new MockStory();
    this.dispatcher = _.clone(Backbone.Events);
    this.view = new storybase.builder.views.PublishTodoView({
      model: this.story,
      dispatcher: this.dispatcher
    });
    this.subview1 = new this.MockNotCompletedView({
      title: "Incomplete step 1"
    });
    this.subview2 = new this.MockCompletedView({
      title: "Complete step 2"
    });
    this.subview3 = new this.MockNotCompletedView({
      title: "Incomplete step 3"
    });
    this.subview4 = new this.MockCompletedView({
      title: "Complete step 4"
    });
  });

  describe("when a registered event is received", function() {
    it("calls the update method", function() {
      this.view.register(this.subview1, "mockevent");
      spyOn(this.view, 'update');
      this.dispatcher.trigger("mockevent");
      expect(this.view.update).toHaveBeenCalled();
    });
  });

  describe("when all registered steps have been completed", function() {
    beforeEach(function() {
      this.view.register(this.subview2, "mockevent1");
      this.view.register(this.subview4, "mockevent2");
      this.dispatcher.trigger('mockevent1');
    });

    it("the ready method returns true", function() {
      expect(this.view.ready()).toBeTruthy();
    });

    it("no steps are listed in the rendered output", function() {
      this.view.render();
      expect(this.view.$el.html()).toNotContain(this.subview2.options.title);  
      expect(this.view.$el.html()).toNotContain(this.subview4.options.title);  
    });
  });

  describe("when any of the registered steps have not been completed", function() {
    beforeEach(function() {
      this.view.register(this.subview1, "mockevent1");
      this.view.register(this.subview2, "mockevent2");
      this.view.register(this.subview4, "mockevent3");
      this.dispatcher.trigger('mockevent1');
    });

    it("the ready method returns false", function() {
      expect(this.view.ready()).toBeFalsy();
    });

    it("shows incomplete steps in the rendered output", function() {
      this.view.render();
      expect(this.view.$el.html()).toContain(this.subview1.options.title);
      expect(this.view.$el.html()).toNotContain(this.subview2.options.title);
      expect(this.view.$el.html()).toNotContain(this.subview4.options.title);
    });
  });
});

describe('PublishedButtonsView', function() {
  beforeEach(function() {
    this.story = new MockStory();
    this.dispatcher = _.clone(Backbone.Events);
    this.view = new storybase.builder.views.PublishedButtonsView({
      model: this.story,
      dispatcher: this.dispatcher
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

    describe("clicking on the view button", function() {
      beforeEach(function() {
        var $button = this.view.render().$('a,button').filter(':contains("View")');
        spyOn(window, 'open');
        $button.click();
        this.url = $button.attr('href'); 
      });

      it('opens the story in a new window', function() {
        expect(window.open).toHaveBeenCalledWith(this.url);
      });
    });
  });
});

describe('LegalView', function() {
  beforeEach(function() {
    var MockStory = Backbone.Model.extend({});
    this.story = new MockStory();
    this.dispatcher = _.clone(Backbone.Events);
  });

  describe('when initialized with an unpublished story', function() {
    beforeEach(function() {
      this.story.set('status', 'draft');
      this.view = new storybase.builder.views.LegalView({
        dispatcher: this.dispatcher,
        model: this.story
      });
    });

    it('should display with no check boxes checked', function() {
      expect(this.view.render().$('[type="checkbox"]').length).toEqual(2);
      expect(this.view.render().$(':checked').length).toEqual(0);
    });
  });

  describe('when initialized with an published story', function() {
    beforeEach(function() {
      this.story.set('status', 'published');
      this.view = new storybase.builder.views.LegalView({
        dispatcher: this.dispatcher,
        model: this.story
      });
    });

    it('should display with both check boxes checked', function() {
      expect(this.view.render().$('[type="checkbox"]').length).toEqual(2);
      expect(this.view.render().$(':checked').length).toEqual(2);
    });
  });

  describe('when only the first checkbox is checked', function() {
    beforeEach(function() {
      this.story.set('status', 'draft');
      this.view = new storybase.builder.views.LegalView({
        dispatcher: this.dispatcher,
        model: this.story
      });
      this.spy = sinon.spy();
      this.dispatcher.on("accept:legal", this.spy);
      this.view.render().$('[type="checkbox"]').first().prop('checked', true).trigger('change');
    });

    it('should not trigger the "accept:legal" event', function() {
      expect(this.view.$(':checked').length).toEqual(1);
      expect(this.spy.called).toBeFalsy();
    });
  });

  describe('when only the second checkbox is checked', function() {
    beforeEach(function() {
      this.story.set('status', 'draft');
      this.view = new storybase.builder.views.LegalView({
        dispatcher: this.dispatcher,
        model: this.story
      });
      this.spy = sinon.spy();
      this.dispatcher.on("accept:legal", this.spy);
      this.view.render().$('[type="checkbox"]').eq(1).prop('checked', true).trigger('change');
    });

    it('should not trigger the "accept:legal" event', function() {
      expect(this.view.$(':checked').length).toEqual(1);
      expect(this.spy.called).toBeFalsy();
    });
  });

  describe('when both checkboxes are checked', function() {
    beforeEach(function() {
      this.story.set('status', 'draft');
      this.view = new storybase.builder.views.LegalView({
        dispatcher: this.dispatcher,
        model: this.story
      });
      this.spy = sinon.spy();
      this.dispatcher.on("accept:legal", this.spy);
      this.view.render().$('[type="checkbox"]').prop('checked', true).trigger('change');
    });

    it('should not trigger the "accept:legal" event', function() {
      expect(this.view.$(':checked').length).toEqual(2);
      expect(this.spy.called).toBeTruthy();
    });
  });
});

describe('LicenseView', function() {
  beforeEach(function() {
    this.story = new MockStory();
    this.dispatcher = _.clone(Backbone.Events);
  });

  describe('when initialized with a model with a CC BY license', function() {
    beforeEach(function() {
      this.story.set('license', 'CC BY');
      this.view = new storybase.builder.views.LicenseView({
        dispatcher: this.dispatcher,
        model: this.story
      });
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
        dispatcher: this.dispatcher,
        model: this.story
      });
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
