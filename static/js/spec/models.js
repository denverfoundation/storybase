describe('Story model', function() {
  beforeEach(function() {
    this.server = sinon.fakeServer.create();
    this.storyId = '357c5885c4e844cb8a4cd4eebe912a1c';
    this.fixture = this.fixtures.Sections[this.storyId];
    this.server.respondWith(
      "GET",
      "/api/0.1/stories/" + this.storyId + "/sections/",
      this.validResponse(this.fixture)
    );
  });

  afterEach(function() {
    this.server.restore();
  });

  describe('when getting its sections', function() {
    it('should return a collection of sections to a callback', function() {
      var that = this;
      var fetchSucceeded = false;
      var story = new storybase.models.Story({
        story_id: this.storyId 
      });
      story.fetchSections({
        success: function(sections) {
          fetchSucceeded = true;
          expect(sections.url).toEqual('/api/0.1/stories/' + story.id + '/sections/');
          expect(sections.length).toEqual(that.fixture.objects.length);
        }
      });
      this.server.respond();
      expect(fetchSucceeded).toEqual(true);
    });
  });

  describe('when new', function() {
    it("doesn't have an id in the url", function() {
      var story = new storybase.models.Story;
      expect(story.url()).toEqual('/api/0.1/stories/');
    });
  });
});
