from storybase_story.models import create_story

class StoryListWidgetViewTestMixin(object): 
    """
    TestCase mixin for testing subclasses of `StoryListWidgetView`

    The ``setUp()`` method of the TestCase that mixes in this class
    must define ``self.obj`` as the aggregating model for the list
    view and ``self.related_field_name`` as the name of the related
    field on the ``Story`` model.

    Finally, the ``setUp()`` method should call ``set_up_stories()``
    
    """
    def set_up_stories(self):
        self.stories = []
        for i in range(1, 5):
            title = "Test widget story %d" % i
            summary = "Test widget story summary %d" % i
            byline = "Test author %d" % i
            story = create_story(title=title, summary=summary, byline=byline, status='published')
            related_field = getattr(story, self.related_field_name)
            related_field.add(self.obj)
            self.stories.append(story)

    def get_obj_url(self):
        return self.obj.get_absolute_url()

    def test_get(self):
        response = self.client.get('%swidget/' % self.get_obj_url())
        self.assertEqual(response.context['object'], self.obj)
        self.assertEqual(len(response.context['stories']), 3)
        self.assertNotIn(self.stories[0], response.context['stories'])
        for i in range(1, 4):
            self.assertIn(self.stories[i], response.context['stories'])

    def test_get_not_found(self):
        path = self.get_obj_url()
        path = path.replace(self.obj.slug, 'invalid-slug')
        response = self.client.get('%swidget/' % path)
        self.assertEqual(response.status_code, 404)
