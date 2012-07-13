describe('SectionAssetEditView view', function() {
  beforeEach(function() {
    jasmine.getFixtures().fixturesPath = 'spec/fixtures';
    loadFixtures('builder_templates.html');
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

  describe('when rendering', function(){
    beforeEach(function() {
      this.view.render();
    });

    describe('with an undefined type property', function() {
      it('should provide a list of available asset types', function() {
        expect(_.size(this.view.$('.asset-type'))).toEqual(_.size(this.assetTypes));
      });
    });
  });

});
