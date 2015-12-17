

describe('TastypieMixin collection mixin', function() {
  beforeEach(function() {
    this.collectionClass = Backbone.Collection.extend(
      _.extend({}, storybase.collections.TastypieMixin)
    );
    this.collection = new this.collectionClass();
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

describe('DataSet model', function() {
  beforeEach(function() {
    this.model = new storybase.models.DataSet();
  });

  describe('validate method', function() {
    it('should return errors when no attributes is present', function() {
      var attrs = {};
      var errs = this.model.validate(attrs);
      expect(errs.title).toBeDefined();
      expect(errs.file).toBeDefined();
      expect(errs.url).toBeDefined();
    });

    it('should return errors when neither the file nor url attribute is present', function() {
      var attrs = {
        title: 'Dataset title'
      };
      var errs = this.model.validate(attrs);
      expect(errs.title).toBeUndefined();
      expect(errs.file).toBeDefined();
      expect(errs.url).toBeDefined();
    });

    it('should return errors when both a file and url attribute are present', function() {
      var attrs = {
        title: 'Dataset title',
        file: 'mock file',
        url: 'http://codataengine.org/find/physically-active-rate-race-county-metro-denver-region-2009'
      };
      var errs = this.model.validate(attrs);
      expect(errs.title).toBeUndefined();
      expect(errs.file).toBeDefined();
      expect(errs.url).toBeDefined();
    });

    it('should not return errors when only a file or url is present', function() {
      var attrs = {
        title: 'Dataset title',
        file: 'mock file'
      };
      var errs = this.model.validate(attrs);
      expect(errs).toBeUndefined();
      delete attrs.file;
      attrs.url = 'http://codataengine.org/find/physically-active-rate-race-county-metro-denver-region-2009';
      errs = this.model.validate(attrs);
      expect(errs).toBeUndefined();
    });

    it('should not return errors when no file is present for an existing dataset', function() {
      this.model.id = '501593a0-d372-11e2-8b8b-0800200c9a66';
      this.model.set('file', 'mock file');
      var attrs = {
        'title': 'New title'
      };
      var errs = this.model.validate(attrs);
      expect(errs).toBeUndefined();
    });
  });
});

describe('DataSets collection', function() {
  beforeEach(function() {
    this.collection = new storybase.collections.DataSets();
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

  describe('A collection associated with an asset', function() {
    beforeEach(function() {
      this.asset = new Backbone.Model({
        id: '78b26070d5d211e19b230800200c9a66'
      });
      this.collection.setAsset(this.asset);
    });

    it('should have a URL of "/api/0.1/datasets/assets/<asset_id>/"', function() {
      expect(this.collection.url()).toEqual('/api/0.1/datasets/assets/' + this.asset.id + '/');
    });
  });
});

describe("Section model", function() {
  describe("when new", function() {
    it("should have an assets collection", function() {
      this.section = new storybase.models.Section();
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

describe("Sections collection", function() {
  describe("fetchAssets method", function() {
    beforeEach(function() {
      this.server = sinon.fakeServer.create();
      this.sectionsFixture = this.fixtures.Sections.getList["6c8bfeaa6bb145e791b410e3ca5e9053"];
      this.collection = new storybase.collections.Sections();
      this.collection.url = "/api/0.1/stories/6c8bfeaa6bb145e791b410e3ca5e9053/sections/";
      this.collection.reset(this.sectionsFixture.objects);
    });

    afterEach(function() {
      this.server.restore();
    });

    describe("when the server returns a valid response", function() {
      beforeEach(function() {
        this.server.respondWith(
          "GET",
          this.collection.url,
          this.validResponse(this.sectionsFixture)
        );
        _.each(this.sectionsFixture.objects, function(section) {
          var sectionId = section.section_id;
          var url = this.collection.url + sectionId + "/assets/";
          this.server.respondWith(
            "GET",
            url,
            this.validResponse(this.fixtures.SectionAssets.getList[sectionId])
          );
        }, this);
      });

      it("should populate each section's assets collection", function() {
        var spec = this;
        var checkAssertions = function() {
          spec.collection.each(function(section) {
            var fixture = spec.fixtures.SectionAssets.getList[section.id];
            expect(section.assets.length).toEqual(fixture.objects.length);
            _.each(fixture.objects, function(assetJSON) {
              var asset = section.assets.get(assetJSON.asset.asset_id);
              expect(asset).toBeDefined();
            });
          });
        };
        var callback = sinon.spy(checkAssertions);
        this.collection.fetchAssets({
          success: callback
        });
        this.server.respond();
        expect(callback.called).toBe(true);
      });
    });

    describe("when the server doesn't respond", function() {
      it("should execute an error callback", function() {
        var errorCallback = sinon.spy();
        var successCallback = sinon.spy();
        this.collection.fetchAssets({
          success: successCallback,
          error: errorCallback
        });
        this.server.respond();
        expect(errorCallback.called).toBe(true);
        expect(successCallback.called).toBe(false);
      });

      it("should have empty asset collections", function() {
        var spec = this;
        var errorCallback = sinon.spy(function() {
          spec.collection.each(function(section) {
            expect(section.assets.length).toEqual(0);
          });
        });
        this.collection.fetchAssets({
          error: errorCallback
        });
        this.server.respond();
        expect(errorCallback.called).toBe(true);
      });
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
      this.story = new storybase.models.Story();
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
      var templateFixture = this.fixtures.Stories.getDetail["0b2b9e3f38e3422ea3899ee66d1e334b"];
      var templateSectionsFixture = this.fixtures.Sections.getList[templateFixture.story_id];
      var templateStory = new storybase.models.Story(templateFixture);
      var story = new storybase.models.Story();
      var storyProps = ['structure_type'];
      var storySuggestedProps = ['summary', 'call_to_action'];
      var sectionProps = ['layout', 'root', 'layout_template', 'help'];
      templateStory.sections.reset(templateSectionsFixture.objects);

      expect(story.id == templateStory.id).toBe(false);
      story.fromTemplate(templateStory);
      _.each(storyProps, function(prop) {
        expect(story.get(prop)).toEqual(templateStory.get(prop));
      });
      _.each(storySuggestedProps, function(prop) {
        expect(story.get(prop + '_suggestion')).toEqual(templateStory.get(prop));
      });
      expect(story.get('template_story')).toEqual(templateStory.get('story_id'));
      expect(story.sections.length).toBeTruthy();
      templateStory.sections.each(function(section) {
        var sectionCopy = story.sections.where({
          title_suggestion: section.get('title')
        })[0];
        expect(sectionCopy).toBeDefined();
        expect(sectionCopy.get('title')).toEqual('');
        _.each(sectionProps, function(prop) {
          expect(sectionCopy.get(prop)).toEqual(section.get(prop));
        });
        expect(sectionCopy.get('template_section')).toEqual(section.get('section_id'));
        expect(sectionCopy.get('weight')).toEqual(section.get('weight') - 1);
      });
    });
  });

  describe('validateStory method', function() {
    var MockFeaturedAssets = Backbone.Collection.extend({
      save: function(options) {},

      setStory: function(story) {}
    });

    beforeEach(function() {
      this.story = new storybase.models.Story();
    });

    it('returns an error when the story has no title', function() {
      var validation = this.story.validateStory();
      expect(validation).toBeDefined();
      expect(validation.errors.title).toBeDefined();
    });

    it('returns a warning when the story has no byline', function() {
      var validation = this.story.validateStory();
      expect(validation).toBeDefined();
      expect(validation.warnings.byline).toBeDefined();
    });

    it('returns a warning when the story has no summary', function() {
      var validation = this.story.validateStory();
      expect(validation).toBeDefined();
      expect(validation.warnings.summary).toBeDefined();
    });

    it('returns a warning when the story has no featured image', function() {
      var validation = this.story.validateStory();
      expect(validation).toBeDefined();
      expect(validation.warnings.featuredAsset).toBeDefined();
    });

    it('returns nothing when all required fields are set', function() {
      this.story.set('title', "Test Title");
      this.story.set('byline', "Test Author");
      this.story.set('summary', "Test summary");
      this.story.setFeaturedAssets(new MockFeaturedAssets());
      this.story.setFeaturedAsset(new Backbone.Model());
      var validation = this.story.validateStory();
      expect(validation).toBeUndefined();
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
      this.model.on("invalid", this.spy);
    });

    it('should fail validation', function() {
      this.model.set('url', 'http://example.com/asset/url/', {validate: true});
      this.model.set('image', '/home/example/image.png', {validate: true});
      expect(this.spy).toHaveBeenCalled();
    });
  });
});

describe('Tag model', function() {
  describe('isNew method', function() {
    it('should return true for a model constructed with no attributes', function() {
      this.model = new storybase.models.Tag();
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
        this.collection = new Backbone.Collection();
        this.collection.url = '/api/0.1/tags/stories/472d5039b37748ba8d78d685aa898475/';
        this.collection.add(this.model);
        expect(this.model.url()).toEqual(this.collection.url);
      });
    });
  });
});

describe('StoryRelations collection', function() {
  describe('A collection associated with a story', function() {
    beforeEach(function() {
      // Mock the story model's URL property
      var Story = Backbone.Model.extend({
        url: '/api/0.1/stories/78b26070d5d211e19b230800200c9a66/'
      });
      this.story = new Story({
        id: '78b26070d5d211e19b230800200c9a66'
      });
      this.collection = new storybase.collections.StoryRelations([], {
        story: this.story
      });
    });

    it('should have a URL of "/<story_url>/related/"', function() {
      // Make sure our mock URL is sane
      expect(_.result(this.story, 'url')).toEqual('/api/0.1/stories/' + this.story.id + '/');
      expect(this.collection.url()).toEqual(_.result(this.story, 'url') + 'related/');
    });
  });
});
