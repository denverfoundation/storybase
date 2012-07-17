describe('BuilderView', function() {
  beforeEach(function() {
    this.dispatcher = _.clone(Backbone.Events);
    this.view = new storybase.builder.views.BuilderView({
      dispatcher: this.dispatcher
    });
  });

  describe('when receiving the "error" event', function() {
    beforeEach(function() {
      // Binding event handlers to the dispatcher happens in the view's
      // initialize method, so we have to spy on the prototype so the
      // spied method will get bound.
      spyOn(storybase.builder.views.BuilderView.prototype, 'error');
      this.view = new storybase.builder.views.BuilderView({
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
    jasmine.getFixtures().fixturesPath = 'spec/fixtures';
    loadFixtures('story_builder_handlebars.html');
    this.dispatcher = _.clone(Backbone.Events);
    this.view = new storybase.builder.views.SectionEditView({
      dispatcher: this.dispatcher,
      model: new Backbone.Model(),
      story: new Backbone.Model()
    });
  });

  describe('when initializing', function() {
    it('should have an assets property', function() {
      expect(this.view.assets).toBeDefined();
    });
  });

  describe('when initialized with an existing story and section', function () {
    beforeEach(function() {
      var Section = Backbone.Model.extend({
        url: function() {
          return '/api/0.1/stories/357c5885c4e844cb8a4cd4eebe912a1c/sections/dc044f23e93649d6b1bd48625fc301cd/'
        }
      });
      var Story = Backbone.Model.extend({
        url: function() {
          return '/api/0.1/stories/357c5885c4e844cb8a4cd4eebe912a1c/';
        }
      });
      this.view = new storybase.builder.views.SectionEditView({
        dispatcher: this.dispatcher,
        model: new Section({
          id: "dc044f23e93649d6b1bd48625fc301cd",
          layout_template: "<div class=\"section-layout side-by-side\">\n    <div class=\"left\">\n        <div class=\"storybase-container-placeholder\" id=\"left\"></div>\n    </div>\n    <div class=\"right\">\n        <div class=\"storybase-container-placeholder\" id=\"right\"></div>\n    </div>\n</div>\n",
        }), 
        story: new Story(), 
        templateSource: $('#section-edit-template').html()
      });
    });

    describe('when rendering', function() {
      beforeEach(function() {
        this.server = sinon.fakeServer.create();
        this.fixture = this.fixtures.SectionAssets.getList;
        this.server.respondWith(
          "GET",
          '/api/0.1/stories/357c5885c4e844cb8a4cd4eebe912a1c/sections/dc044f23e93649d6b1bd48625fc301cd/assets/',
          this.validResponse(this.fixture)
        );
      });

      afterEach(function() {
        this.server.restore();
      });

      it('should display the assets', function() {
        this.view.render();
        this.server.respond();
        expect(this.view.$el.html()).toContain(this.fixture.objects[0].asset.content);
        expect(this.view.$el.html()).toContain(this.fixture.objects[1].asset.content);
      });
    });
  });

  describe('when receiving the "add:asset" event', function() {
    beforeEach(function() {
      this.asset = new Backbone.Model({
         id: 'bef53407591f4fd8bd169f9cc02672f9',
         type: 'text',
         body: 'Test text asset body',
         content: 'Test text asset body'
      });
      this.dispatcher.trigger('add:asset', this.asset); 
    });

    it('should add the asset to the assets collection', function() {
      expect(this.view.assets.size()).toEqual(1);
      expect(this.view.assets.at(0)).toEqual(this.asset);
    });
  
  });
});

describe('SectionAssetEditView view', function() {
  beforeEach(function() {
    // Load Handlebars templates from a fixture file
    // You need to run ./manage.py collectjstemplates to copy the Handlebars
    // templates from the Django template directory to a place where
    // the jasmine-jquery file can find them.  Not awesome, but the most
    // DRY way I could think of that wasn't too much work.
    jasmine.getFixtures().fixturesPath = 'spec/fixtures';
    loadFixtures('story_builder_handlebars.html');
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
       dispatcher: this.dispatcher,
       assetTypes: this.assetTypes,
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
        expect(_.size(this.view.$('.asset-type'))).toEqual(_.size(this.assetTypes));
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
           expect(_.size(this.view.$('.asset-type'))).toEqual(_.size(this.assetTypes));
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
        this.dispatcher.on("add:asset", this.spy);
        this.view.render();
        this.view.$('textarea[name="body"]').val(this.assetBody);
        this.view.$('input[type="submit"]').click();
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

      it('should send the "add:asset" event through the dispatcher', function() {
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

