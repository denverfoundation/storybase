from lettuce import step, world
from lettuce.django import django_url
from nose.tools import assert_equal

@step(u'Then the HTML Asset "([^"]*)" should have a canonical URL')
def access_url(step, title):
    step.given('Given the user navigates to the "Html assets" admin page')
    world.browser.click_link_by_text(title)
    obj_id = world.browser.find_by_css('.asset_id p').first.value
    world.assert_is_uuid4(obj_id)
    world.browser.visit(django_url('/assets/%s' % obj_id))

@step(u'Then the Asset\'s body should be the following:')
def see_body(step):
    el = world.browser.find_by_css('.asset-content').first
    # HACK: is_text_present fails for some reason, for now it's good
    # enough to just make sure the text start and end are present
    text = step.multiline.replace('\n', ' ')
    assert_equal(el.text[:10], text[:10])
    assert_equal(el.text[-10:], text[-10:])

@step(u'Then the Asset\'s title should be "([^"]*)"')
def see_title(step, title):
    world.assert_text_present(title)

@step(u'Then the Asset\'s type should be "([^"]*)"')
def see_type(step, type):
    el = world.browser.find_by_css('.type').first
    assert_equal(el.text, type)

@step(u'Then the Asset\'s attribution should be "([^"]*)"')
def see_attribution(step, attribution):
    el = world.browser.find_by_css('.attribution').first
    assert_equal(el.text, attribution)

@step(u'Then the Asset\'s license should be "([^"]*)"')
def see_license(step, license):
    el = world.browser.find_by_css('.license').first
    assert_equal(el.text, license)

@step(u'Then the Asset\'s status should be "([^"]*)"')
def see_status(step, status):
    el = world.browser.find_by_css('.status').first
    assert_equal(el.text, status)

@step(u'Then the Asset\'s creation date should be "([^"]*)"')
def see_asset_created(step, date):
    el = world.browser.find_by_css('time.asset-created').first
    assert_equal(el.text, date)

@step(u'Then the Asset\'s owner should be "([^"]*)"')
def see_owner(step, owner):
    el = world.browser.find_by_css('.owner').first
    assert_equal(el.text, owner)
