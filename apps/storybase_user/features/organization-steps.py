from datetime import datetime
from lettuce import step, world
from lettuce.django import django_url
from nose.tools import assert_not_equal, assert_true

@step(u'Given an admin user creates the Organization "([^"]*)" with website URL "([^"]*)"')
def create(step, name, website_url):
    world.create_admin_user()
    world.admin_login()
    world.browser.click_link_by_href("storybase_user/organization/add/")
    world.browser.fill('name', name)
    world.browser.fill('website_url', website_url)
    world.browser.find_by_name('_save').first.click()

@step(u'Then the Organization should have a canonical URL')
def access_url(step):
    organization_id = world.browser.find_by_css(',form_row.organization_id p').value
    world.assert_is_uuid(organization_id)
    world.browser.visit(django_url('/organizations/%s' % organization_id))

@step(u'Then the Organization\'s website should be listed as "([^"]*)"')
def see_website_url(step, website_url):
    world.assert_text_present(website_url)

@step(u'Then the Organization\'s members list should be blank')
def no_members(step):
    world.assert_text_not_present('Members')

@step(u'Then the Organization\'s created on field should be set to the current date')
def created_today(step):
    created = datetime.strptime(world.browser.find_by_css('time.created').value,
        '%B %d, %Y')
    world.assert_today(created)

@step(u'Then the Organization\'s last edited field should be set to within 1 minute of the current date and time')
def last_edited_now(step):
    last_edited = datetime.strptime(world.browser.find_by_css('time.last_edited').value,
        '%B %d, %Y %I:%M %p')
    world.assert_now(last_edited, 60)

@step(u'Then the Organization\'s description should be blank')
def blank_description(step):
    world.assert_text_not_present('Description')
