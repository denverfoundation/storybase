describe('SectionAssetEditView view', function() {
  beforeEach(function() {
    this.view = new storybase.builder.views.SectionAssetEditView({});
  });

  describe('when initializing', function() {

    it('should have an undefined model property', function() {
      expect(this.view.model).toBeUndefined();
    });

    it('should have an undefined type property', function() {
      expect(this.view.type).toBeUndefined();
    });
  });
});
