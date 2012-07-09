describe('Section collection', function() {
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

  describe('when initialized with a story', function() {
    it('should have a URL relative to the story URL', function() {
      var story = new storybase.models.Story({
        story_id: this.storyId
      });
      var sections = new storybase.collections.Sections([], {
        story: story
      });
      expect(sections.url()).toEqual('/api/0.1/stories/' + story.id + '/sections/');
    });

    it("should be able to fetch the story's sections", function() {
      var story = new storybase.models.Story({
        story_id: this.storyId
      });
      var sections = new storybase.collections.Sections([], {
        story: story
      });
      sections.fetch();
      this.server.respond();
      expect(sections.length).toEqual(this.fixture.objects.length);
    })
  });
});

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
          expect(sections.url()).toEqual('/api/0.1/stories/' + story.id + '/sections/');
          expect(sections.length).toEqual(that.fixture.objects.length);
        }
      });
      this.server.respond();
      expect(fetchSucceeded).toEqual(true);
    });
  });
});

describe('Story model', function() {
  describe('when new', function() {
    it("doesn't have an id in the url", function() {
      var story = new storybase.models.Story;
      expect(story.url()).toEqual('/api/0.1/stories/');
    });
  });
});
