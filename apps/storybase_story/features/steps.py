from lettuce import step

from storybase_story.models import create_story, Story

@step(u'Given a Story with title "([^"]*)" has been created')
def story_created(step, title):
    create_story(title)

@step(u'Given a Story with title "([^"]*)" has been published')
def story_published(step, title):
    story = Story.objects.get(storytranslation__title=title)
    story.status = 'published'
    story.save()
