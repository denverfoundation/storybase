from lettuce import before, step, world
from lettuce.django import django_url
from storybase_user.models import Organization, Project

@before.each_scenario
def setup_organization(scenario):
    matching_scenarios = ('Admin can create a new Project',)
    if scenario.name in matching_scenarios: 
        world.create_organization("Mile High Connects") 

@step(u'Given the admin sets the Project name to  "([^"]*)"')
def set_name(step, name):
    world.browser.fill('name', name)
    if hasattr(world, 'project_changed'):
        world.project_changed.append('name')

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
    world.assert_text_in_list('ul.members li', org_name)

@step(u'Then the Organization\'s stories list should be blank')
def no_stories_list(step):
    world.assert_text_not_present("Stories")
