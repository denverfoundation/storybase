"""Steps used throughout lettuce tests for story app"""

from lettuce import step, world

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
