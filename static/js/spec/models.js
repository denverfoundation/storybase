describe('TastypieMixin collection mixin', function() {
  beforeEach(function() {
    this.collectionClass = Backbone.Collection.extend(
      _.extend({}, storybase.collections.TastypieMixin)
    );
    this.collection = new this.collectionClass;
  });

  it('should parse its model objects from an "objects" property of the response', function() {
    var objects = [
      {
        id: '78b26070d5d211e19b230800200c9a66',
        title: 'Test Title 1'
      },
      {
        id: '9a38f580d5d511e19b230800200c9a66',
        title: 'Test Title 2'
      }
    ];
    var mockResponse = {
      objects: objects 
    };
    expect(this.collection.parse(mockResponse)).toEqual(objects);
  });
});

describe('DataSets collection', function() {
  beforeEach(function() {
    this.collection = new storybase.collections.DataSets;
  });

  describe('A newly created collection', function() {
    it('should have a URL of "/api/0.1/datasets/"', function() {
      expect(this.collection.url()).toEqual('/api/0.1/datasets/');
    });
  });

  describe('A collection associated with a story', function() {
    beforeEach(function() {
      this.story = new Backbone.Model({
        id: '78b26070d5d211e19b230800200c9a66'
      });
      this.collection.setStory(this.story);
    });

    it('should have a URL of "/api/0.1/datasets/stories/<story_id>/"', function() {
      expect(this.collection.url()).toEqual('/api/0.1/datasets/stories/' + this.story.id + '/');
    });
  });
});

describe("Section model", function() {
  describe("when new", function() {
    it("should have an assets collection", function() {
      this.section = new storybase.models.Section;
      expect(this.section.assets).toBeDefined();
      expect(this.section.assets.length).toEqual(0);
    });
  });

  describe("when initialized with attributes", function() {
    beforeEach(function() {
      var storyId = "0b2b9e3f38e3422ea3899ee66d1e334b";
      this.fixture = this.fixtures.Sections.getList[storyId].objects[0];
      this.section = new storybase.models.Section(this.fixture);
    });

    it('should have the asset collection URL initialized', function() {
      expect(this.section.assets.url).toEqual(this.section.url() + 'assets/');
    });
  });
});

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

  describe('when new', function() {
    beforeEach(function() {
      this.story = new storybase.models.Story;
    });

    it("doesn't have an id in the url", function() {
      expect(this.story.url()).toEqual('/api/0.1/stories/');
    });

    it("has a sections property", function() {
      expect(this.story.sections).toBeDefined();
      expect(this.story.sections.length).toEqual(0);
    });
  });

  describe('fromTemplate method', function() {
    it("copies selected attributes from another story", function() {
      var templateFixture = this.fixtures.Stories.explainerTemplate;
      var templateSectionsFixture = this.fixtures.Sections.getList[templateFixture['story_id']];
      var templateStory = new storybase.models.Story(templateFixture);
      var story = new storybase.models.Story;
      var storyProps = ['structure_type', 'summary', 'call_to_action'];
      var sectionProps = ['title', 'layout', 'root', 'layout_template', 'help'];
      templateStory.sections.reset(templateSectionsFixture.objects);

      expect(story.id == templateStory.id).toBe(false);
      story.fromTemplate(templateStory);
      _.each(storyProps, function(prop) {
        expect(story.get(prop)).toEqual(templateStory.get(prop));
      });
      expect(story.sections.length).toBeTruthy();
      expect(story.sections.length).toEqual(templateStory.sections.length);
      templateStory.sections.each(function(section) {
        var sectionCopy = story.sections.where({
          title: section.get('title')
        })[0];
        expect(sectionCopy).toBeDefined();
        _.each(sectionProps, function(prop) {
          expect(sectionCopy.get(prop)).toEqual(section.get(prop));
        });
        expect(sectionCopy.get('weight')).toEqual(section.get('weight') - 1);
      });
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

  describe('when the image and url attributes are set', function() {
    beforeEach(function() {
      this.model = new storybase.models.Asset({
        type: 'text'
      });
      this.spy = jasmine.createSpy();
      this.model.on("error", this.spy);
    });

    it('should fail validation', function() {
      this.model.set('url', 'http://example.com/asset/url/');
      this.model.set('image', '/home/example/image.png');
      expect(this.spy).toHaveBeenCalled();
    });
  });
});

describe('Tag model', function() {
  describe('isNew method', function() {
    it('should return true for a model constructed with no attributes', function() {
      this.model = new storybase.models.Tag;
      expect(this.model.isNew()).toBe(true);
    });

    it('should return true for a model constructed with a tag_id', function() {
      this.model = new storybase.models.Tag({
        "tag_id": "0644b72fc1eb46dba8ed68daff0228d3"
      });
      expect(this.model.isNew()).toBe(true);
    });

    it('should return false for a model with a resource_uri attribute', function() {
      this.model = new storybase.models.Tag({
        "tag_id": "0644b72fc1eb46dba8ed68daff0228d3"
      });
      this.model.set('resource_uri', '/api/0.1/tags/0644b72fc1eb46dba8ed68daff0228d3/stories/472d5039b37748ba8d78d685aa898475'); 
      expect(this.model.isNew()).toBe(false);
    });
  });

  describe('url method', function() {
    describe('when the model instance is new', function() {
      beforeEach(function() {
        this.model = new storybase.models.Tag({
          "tag_id": "0644b72fc1eb46dba8ed68daff0228d3"
        });
      });
      it('should return the collection url', function() {
        this.collection = new Backbone.Collection;
        this.collection.url = '/api/0.1/tags/stories/472d5039b37748ba8d78d685aa898475/';
        this.collection.add(this.model);
        expect(this.model.url()).toEqual(this.collection.url);
      });
    });
  });
});
