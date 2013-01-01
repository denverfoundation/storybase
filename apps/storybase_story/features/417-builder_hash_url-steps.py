# -*- coding: utf-8 -*-
from time import sleep

from lettuce import step, world
from lettuce.django import django_url

from nose.tools import assert_equal

from django.core.urlresolvers import reverse

from storybase_story.models import Story

#import logging
#logger = logging.getLogger('storybase')

@step(u'Given the user opens the Story "([^"]*)" in the story builder with a hashed story ID')
def open_story_in_builder_hash_id(step, title):
    story = Story.objects.get(storytranslation__title=title)
    path = reverse('story_builder', kwargs={'story_id': story.story_id})
    path = path.replace(story.story_id, "#%s" % (story.story_id))
    world.browser.visit(django_url(path))

@step(u'Given the user opens the connected Story "([^"]*)" in the story builder with a hashed story ID')
def open_connected_story_in_builder_hash_id(step, title):
    story = Story.objects.get(storytranslation__title=title)
    connected_to_story = story.connected_to_stories()[0]
    path = reverse('connected_story_builder',
            kwargs={'story_id': story.story_id,
                    'source_story_id': connected_to_story.story_id})
    path = path.replace(story.story_id, "#%s" % (story.story_id))
    world.browser.visit(django_url(path))

@step(u'Then the user should be redirected to the story builder for the Story "([^"]*)" without a hashed story ID in the URL')
def has_story_builder_path_no_hash(step, title):
    story = Story.objects.get(storytranslation__title=title)
    path = reverse('story_builder', kwargs={'story_id': story.story_id})
    # Sleep to give the browser time to reload before checking the URL
    sleep(1)
    assert_equal(world.browser.url, django_url(path))

@step(u'Then the user should be redirected to the connected story builder for the Story "([^"]*)" without a hashed story ID in the URL')
def has_connected_story_builder_path_no_hash(step, title):
    story = Story.objects.get(storytranslation__title=title)
    connected_to_story = story.connected_to_stories()[0]
    path = reverse('connected_story_builder',
            kwargs={'story_id': story.story_id,
                    'source_story_id': connected_to_story.story_id})
    # Sleep to give the browser time to reload before checking the URL
    sleep(1)
    assert_equal(world.browser.url, django_url(path))
