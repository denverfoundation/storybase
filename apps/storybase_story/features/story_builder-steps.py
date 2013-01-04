from lettuce import step, world
from lettuce.django import django_url

from nose.tools import assert_equal

from django.core.urlresolvers import reverse

from storybase_story.models import Story

@step(u'the "([^"]*)" section is present in the table of contents')
def section_in_toc(step, name):
    world.browser.find_by_xpath("//*[@class='section-thumbnail']/*[@class='title' and contains(text(), '%s')]" % (name))

@step(u'the "([^"]*)" workflow step button is present')
def workflow_step_button(step, name):
    world.browser.find_by_xpath("//*[@id='workflow-step']/*[contains(text(), '%s')]" % (name))

@step(u'Then the browser location should include the story ID for the Story "([^"]*)"')
def story_id_in_location(step, title):
    story = Story.objects.get(storytranslation__title=title)
    path = reverse('story_builder', kwargs={'story_id': story.story_id})
    assert_equal(world.browser.url, django_url(path))
                
