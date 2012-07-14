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
  });


  describe('with the type property set to "text"', function() {
    beforeEach(function() {
      this.view.type = 'text';
    });

    describe('when rendering', function(){
      beforeEach(function() {
        this.view.render();
      });

      it('should provide a form for selecting an asset', function() {
        expect(this.view.$el).toContain('form');
      });

      it('should not provide a file and url input', function() {
        expect(this.view.$el).not.toContain('input[name="url"]');
        expect(this.view.$el).not.toContain('input[name="file"]');
      });

      it('should include a textarea', function() {
        expect(this.view.$el).toContain('textarea');
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

      it('should provide a form for selecting an asset', function() {
        expect(this.view.$el).toContain('form');
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
