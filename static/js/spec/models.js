describe('Section collection', function() {
  describe('when initialized with a story', function() {
    it('should have a URL relative to the story URL', function() {
      var story = new storybase.models.Story({
        story_id: '357c5885c4e844cb8a4cd4eebe912a1c' 
      });
      var sections = new storybase.collections.Sections({
        story: story
      });
      expect(sections.url()).toEqual('/api/0.1/stories/' + story.id + '/sections/');
    });
  });
});

describe('Story model', function() {
  describe('when getting its sections', function() {
    it('should return a collection of sections to a callback', function() {
      var story = new storybase.models.Story({
        story_id: '357c5885c4e844cb8a4cd4eebe912a1c' 
      });
      story.getSections({
        success: function(sections) {
          expect(sections.url()).toEqual('/api/0.1/stories/' + story.id + 'sections');
        }
      });
    });
  });
});
