from datetime import datetime
from urlparse import urlparse
from lettuce import before, step, world
from lettuce.django import django_url
from nose.tools import assert_equal
from storybase_user.models import create_organization, create_project

@before.each_scenario
def setup_organization_and_project(scenario):
    matching_scenarios = ('An admin can create a story and it\'s core metadata in English')
    if scenario.name in matching_scenarios: 
        create_organization(name="Mile High Connects") 
        create_project(name='The Metro Denver Regional Equity Atlas')

@step(u'Then the Story "([^"]*)" should have a canonical URL')
def access_url(step, title):
    step.given('Given the user navigates to the "Stories" admin page')
    world.browser.click_link_by_text(title)
    organization_id = world.browser.find_by_css('.story_id p').first.value
    world.assert_is_uuid4(organization_id)
    world.browser.visit(django_url('/stories/%s' % organization_id))

@step(u'Then the Story\'s last edited field should be set to within 1 minute of the current date and time')
def last_edited_now(step):
    last_edited = datetime.strptime(world.browser.find_by_css('time.last-edited').first.value,
        '%B %d, %Y %I:%M %p')
    world.assert_now(last_edited, 60)

@step(u'Then the Story\'s status should be "([^"]*)"')
def see_status_as(step, status):
    world.assert_element_text_equal('p.status', status)

@step(u'Then the Story\'s published date should be blank')
def blank_published_date(step):
    world.assert_text_not_present('Date Published')

@step(r'the Story "([^"]*)" exists')
def exists_in_admin(step, title):
    world.browser.visit(django_url('/admin/storybase_story/story/'))
    world.browser.click_link_by_text(title)
    story_id = world.browser.find_by_css('.story_id p').first.value
    world.save_info('Story', story_id)

@step(u'Given the user navigates to the Story\'s detail page')
def visit_detail_page(step):
    world.browser.visit(django_url('/stories/%s' % world.story.story_id))

@step(u'Given the user navigates to the Story\'s "([^"]*)" detail page')
def visit_translated_detail_page(step, language):
    world.browser.visit(django_url('/%s/stories/%s' % (world.language_lookup(language), world.story.story_id)))

@step(u'Then the user is redirected to the Story\'s "([^"]*)" detail page')
def detail_redirected_page(step, language):
    language_code = world.language_lookup(language)
    parsed_url = urlparse(world.browser.url)
    assert_equal(parsed_url.path, 
        "/%s/stories/%s/" % (language_code, world.story.story_id))

@step(u'Given the user sets Status to "([^"]*)"')
def edit_status(step, status):
    world.browser.select('status', status)

@step(u'Then the Story\'s status is "([^"]*)"')
def see_status(step, status):
    seen_status = world.browser.find_by_css('p.status').first.text
    assert_equal(seen_status, status)

@step(u'Then the Story\'s published field should be set to within 1 minute of the current date and time')
def published_now(step):
    published = datetime.strptime(world.browser.find_by_css('time.published').value,
        '%B %d, %Y %I:%M %p')
    world.assert_now(published, 60)

@step(u'Given the user visits the admin edit page for Story "([^"]*)"')
def visit_admin_edit_page(step, title):
    world.browser.visit(django_url('/admin/storybase_story/story/'))
    world.browser.click_link_by_text(title)
