describe('Story model', function() {
  beforeEach(function() {
    this.server = sinon.fakeServer.create();
    this.storyId = '357c5885c4e844cb8a4cd4eebe912a1c';
    this.fixture = this.fixtures.Sections.getList[this.storyId];
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

describe('Asset model', function() {
  describe('when initialized with a type of "text"', function() {
    beforeEach(function() {
      this.model = new storybase.models.Asset({
        type: 'text'
      });
    });

    describe('a form for the model', function() {
      beforeEach(function() {
        this.form = new Backbone.Form({
          model: this.model
        });
        this.form.render();
      });

      it('should contain a text area for the body', function() {
        expect($(this.form.el).find('textarea[name="body"]')).toExist();
      });

      it('should not contain an input for url', function() {
        expect($(this.form.el).find('input[name="url"]')).not.toExist();
      });
    });
  });

  describe('when initialized with a type of "image"', function() {
    beforeEach(function() {
      this.model = new storybase.models.Asset({
        type: 'image'
      });
    });

    describe('a form for the model', function() {
      beforeEach(function() {
        this.form = new Backbone.Form({
          model: this.model
        });
        this.form.render();
      });

      it('should not contain a text area for the body', function() {
        expect($(this.form.el).find('textarea[name="body"]')).not.toExist();
      });

      it('should contain an input for url', function() {
        expect($(this.form.el).find('input[name="url"]')).toExist();
      });

      it('should contain an input for image', function() {
        expect($(this.form.el).find('input[name="image"]')).toExist();
      });
    });
  });
});
