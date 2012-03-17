from lettuce import step


@step(u'Given the admin sets the Project name to  "([^"]*)"')
def given_the_admin_sets_the_project_name_to_group1(step, group1):
    assert False, 'This step must be implemented'

@step(u'Given the admin selects "([^"]*)" from the list of available organizations')
def given_the_admin_selects_group1_from_the_list_of_available_organizations(step, group1):
    assert False, 'This step must be implemented'

@step(u'Given the admin clicks the Add icon')
def given_the_admin_clicks_the_add_icon(step):
    assert False, 'This step must be implemented'

@step(u'Then the Project should have a canonical URL')
def then_the_project_should_have_a_canonical_url(step):
    assert False, 'This step must be implemented'

@step(u'Then the Project\'s name should be "([^"]*)"')
def then_the_project_s_name_should_be_group1(step, group1):
    assert False, 'This step must be implemented'

@step(u'Then "([^"]*)" should be listed in the Project\'s Organizations list')
def then_group1_should_be_listed_in_the_project_s_organizations_list(step, group1):
    assert False, 'This step must be implemented'

@step(u'Then the Organization\'s stories list should be blank')
def then_the_organization_s_stories_list_should_be_blank(step):
    assert False, 'This step must be implemented'
