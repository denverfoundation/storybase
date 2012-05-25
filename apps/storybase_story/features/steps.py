"""Steps used throughout lettuce tests for story app"""

from datetime import datetime

from lettuce import step, world
from nose.tools import assert_equal

@step(u'Then the Story\'s title should be "([^"]*)"')
def see_title(step, title):
    world.assert_text_present(title)

@step(u'Then the Story\'s summary is listed as the following:')
def see_summary(step):
    world.assert_text_present(step.multiline)

@step(u'Then the Story\'s byline should be "([^"]*)"')
def see_byline(step, byline):
    world.assert_text_present(byline)

@step(u'Then "([^"]*)" should be listed in the Story\'s Organizations list')
def org_in_list(step, org_name):
    world.assert_text_in_list('ul.organizations li', org_name)

@step(u'Then "([^"]*)" should be listed in the Story\'s Projects list')
def proj_in_list(step, proj_name):
    world.assert_text_in_list('ul.projects li', proj_name)

@step(u'the following topics are listed in the Story\'s Topics list')
def topics_in_list(step):
    topic_names = [topic_dict['name'] for topic_dict in step.hashes]
    world.assert_list_equals('ul.topics li', topic_names)

@step(u'Then the Story\'s published date should be set the current date')
def published_today(step):
    date_el = world.browser.find_by_css('time.published').first
    now = datetime.now()
    assert_equal(date_el.text, now.strftime("%B %d, %Y"))

@step(u'Then the Story\'s last edited date should be set to the current date')
def last_edited_today(step):
    date_el = world.browser.find_by_css('time.last-edited').first
    now = datetime.now()
    assert_equal(date_el.text, now.strftime("%B %d, %Y"))

@step(u'Then the Story\'s contributor is "([^"]*)"')
def see_contributor(step, contributor):
    contributor_el = world.browser.find_by_css('.contributor').first
    assert_equal(contributor_el.text, contributor)
