from django.core.management import call_command
from django.core.urlresolvers import reverse

from lettuce import before, step, world

from storybase_story.models import Story, create_story

@before.each_feature
def setup(feature):
    call_command('loaddata', 'section_layouts', interactive=False)
    call_command('loaddata', 'story_templates', interactive=False)

@step(u'Given the connected story "([^"]*)" has been created with prompt "([^"]*)"')
def connected_story_created(step, title, prompt):
    create_story(title=title, connected_prompt=prompt, allow_connected=True)

@step(u'Then the connected story builder is launched for the story "([^"]*)"')
def connected_story_builder_is_launched(step, title):
    story = Story.objects.get(storytranslation__title=title)
    path = reverse('connected_story_builder', kwargs={'source_slug': story.slug})
    world.assert_url_path_equal(world.browser.url, path)
