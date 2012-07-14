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
    this.view = new storybase.builder.views.SectionAssetEditView({
       assetTypes: this.assetTypes,
    });
  });

  describe('when initializing', function() {
    it('should have an undefined model property', function() {
      expect(this.view.model).toBeUndefined();
    });

    it('should have an undefined type property', function() {
      expect(this.view.type).toBeUndefined();
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

      it("should set the type property", function() {
        expect(this.view.type).toEqual(this.selectedType);
      });

      it('should provide a form for selecting an asset', function() {
        expect(this.view.$el).toContain('form');
      });
    });
  });

  describe('with the type property set', function() {
    beforeEach(function() {
      // Set the type property to a type that we don't really care
      // about to test for things that should happen regardless of type
      this.view.type = 'faketype';
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

  describe('with the type property set to "text"', function() {
    beforeEach(function() {
      this.view.type = 'text';
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
        this.view.render();
        this.view.$('textarea').val(this.assetBody);
        this.view.$('input[type="submit"]').click();
        this.server.respond();
      });

      afterEach(function() {
        this.server.restore();
      });

      it('should set and save the model property', function() {
        expect(this.view.model).toBeDefined();
        expect(this.view.model.get('body')).toEqual(this.assetBody);
        expect(this.view.model.get('type')).toEqual('text');
        expect(this.view.model.isNew()).toBeFalsy();
      });

      it("should display the model's body", function() {
        expect(this.view.$el.text()).toContain(this.view.model.get('body'));
      });
    });
  });

  describe('with the type property set to "image"', function() {
    beforeEach(function() {
      this.view.type = 'image';
    });

    describe('when rendering', function(){
      beforeEach(function() {
        this.view.render();
      });

      it('should provide a file and url input', function() {
        expect(this.view.$el).toContain('input[name="url"]');
        expect(this.view.$el).toContain('input[name="file"]');
      });

      it('should not include a textarea', function() {
        expect(this.view.$el).not.toContain('textarea');
      });
    });
  });

  describe('with the model property set to a text asset', function() {
    beforeEach(function() {
       this.view.model = new Backbone.Model({
         id: 'bef53407591f4fd8bd169f9cc02672f9',
         type: 'text',
         body: 'Test text asset body',
         content: 'Test text asset body'
       });
       this.view.render();
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
