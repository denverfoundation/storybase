from datetime import datetime
from lettuce import before, step, world
from lettuce.django import django_url
from storybase_user.models import Organization, Project

@before.each_scenario
def setup_organization(scenario):
    matching_scenarios = ('Admin can create a new Project',)
    if scenario.name in matching_scenarios: 
        world.create_organization("Mile High Connects") 

@step(u'Given the admin selects "([^"]*)" from the list of available organizations')
def select_org(step, org_name):
    user = Organization.objects.get(name=org_name)
    world.browser.select('organizations_old', user.pk)

@step(u'Given the admin clicks the Add icon')
def clicks_org_add_icon(step):
    world.browser.find_by_css('.organizations .selector-add').first.click()

@step(u'Then the Project named "([^"]*)" should have a canonical URL')
def project_canonical_url(step, name):
    project = Project.objects.get(name=name)
    world.browser.visit(django_url('/projects/%s' % project.project_id))

@step(u'Then the Project\'s name should be "([^"]*)"')
def see_project_name(step, name):
    world.assert_text_present(name)

@step(u'Then "([^"]*)" should be listed in the Project\'s Organizations list')
def org_in_list(step, org_name):
    world.assert_text_in_list('ul.organizations li', org_name)

@step(u'Then the Project\'s stories list should be blank')
def no_stories_list(step):
    world.assert_text_not_present("Stories")

@step(u'Then the Project\'s created on field should be set to the current date')
def created_today(step):
    created = datetime.strptime(world.browser.find_by_css('time.created').value,
        '%B %d, %Y')
    world.assert_today(created)

@step(u'Then the Project\'s last edited field should be set to within 1 minute of the current date and time')
def last_edited_now(step):
    last_edited = datetime.strptime(world.browser.find_by_css('time.last-edited').value,
        '%B %d, %Y %I:%M %p')
    world.assert_now(last_edited, 60)

@step(u'Then the Project\'s description should be blank')
def blank_description(step):
    world.assert_text_not_present('Description')

@step(u'Given the Project "([^"]*)" exists')
def exists_in_admin(step, name):
    world.browser.visit(django_url('/admin/storybase_user/project/'))
    world.browser.click_link_by_text(name)
    project_id = world.browser.find_by_css('.project_id p').first.value
    world.save_info('Project', project_id)

@step(u'Given the user navigates to the "([^"]*)" Project edit admin')
def given_the_user_navigates_to_the_group1_project_edit_admin(step, group1):
    assert False, 'This step must be implemented'

@step(u'Given the user navigates to the Project\'s detail page')
def given_the_user_navigates_to_the_project_s_detail_page(step):
    assert False, 'This step must be implemented'

@step(u'Then the Project\'s description is listed as the following:')
def then_the_project_s_description_is_listed_as_the_following(step):
    assert False, 'This step must be implemented'

@step(u'Then all other fields of the Project are unchanged')
def then_all_other_fields_of_the_project_are_unchanged(step):
    assert False, 'This step must be implemented'
