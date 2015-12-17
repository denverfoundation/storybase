from lettuce import step, world
from lettuce.django import django_url
from nose.tools import assert_equal
from splinter.exceptions import ElementDoesNotExist
from django.contrib.auth.models import User
from storybase_user.models import Organization
from storybase_user.utils import format_user_name

@step(u'Given an admin user creates the Organization "([^"]*)" with website URL "([^"]*)" and description "([^"]*)" in the Django admin')
def create(step, name, website_url, description):
    step.given('Given the user navigates to the "Organizations" addition page')
    step.given('Given the user sets the "name" of the "Organization" to "%s"' % name)
    step.given('Given the user sets the "description" of the "Organization" to "%s"' % description)
    step.given('Given the user sets the "website URL" of the "Organization" to "%s"' % website_url)
    step.given('Given the user clicks the save button')

@step(u'Then the Organization "([^"]*)" should have a canonical URL')
def access_url(step, name):
    step.given('Given the user navigates to the "Organizations" admin page')
    world.browser.click_link_by_text(name)
    try:
        # Django 1.3
        organization_id = world.browser.find_by_css('.organization_id p').first.value
    except ElementDoesNotExist:
        # Django 1.4
        organization_id = world.browser.find_by_css('.field-organization_id p').first.value
    world.assert_is_uuid4(organization_id)
    world.browser.visit(django_url('/organizations/%s' % organization_id))

@step(u'Then the Organization\'s website should be listed as "([^"]*)"')
def see_website_url(step, website_url):
    world.assert_text_present(website_url)

@step(u'Then the Organization\'s contributors list should be blank')
def no_contributors(step):
    world.assert_text_not_present('Members')

@step(u'Then the Organization\'s description should be blank')
def blank_description(step):
    world.assert_text_not_present('Description')

@step(u'Given the Organization "([^"]*)" is visible in the Django admin')
def exists_in_admin(step, name):
    # Visit the Organization's admin panel
    world.browser.visit(django_url('/admin/storybase_user/organization/'))
    world.browser.click_link_by_text(name)
    try:
        # Django 1.3
        organization_id = world.browser.find_by_css('.organization_id p').first.value
    except ElementDoesNotExist:
        # Django 1.4
        organization_id = world.browser.find_by_css('.field-organization_id p').first.value
    world.save_info('Organization', organization_id)

@step(u'Then the Organization has the website URL "([^"]*)" in the Django admin')
def has_website_url_in_admin(step, website_url):
    # Visit the Organization's admin panel
    org_website_url = world.browser.find_by_css('#id_website_url').first.value
    assert_equal(org_website_url, website_url)

@step(u'Given the user visits the admin edit page for Organization "([^"]*)"')
def visit_admin_edit_page(step, name):
    world.browser.visit(django_url('/admin/storybase_user/organization/'))
    world.browser.click_link_by_text(name)

@step(u'Then the Organization\'s description is listed as "([^"]*)"')
def see_description(step, description):
    world.assert_text_present(description)

@step(u'Then all other fields of the Organization are unchanged')
def other_fields_unchanged(step):
    """ Check that the an organization's fields are unchanged """
    organization = Organization.objects.get(organization_id=world.organization.organization_id)
    for field in ('organization_id', 'website_url', 'description', 'created'):
        if field not in world.organization_changed:
            assert_equal(getattr(world.organization, field),
                getattr(organization, field))

@step(u'Given an admin assigns "([^"]*)" to the Organization "([^"]*)" in the Django admin')
def assign_user_to_org(step, username, name):
    """ Assign user to organization via the Organization admin """
    user = User.objects.get(username=username)
    world.browser.visit(django_url('/admin/storybase_user/organization/'))
    world.browser.click_link_by_text(name)
    world.browser.select('contributors_old', user.id)
    world.browser.find_by_css('.contributors .selector-add').first.click()
    world.browser.find_by_name('_save').first.click()

@step(u'Given an admin assigns "([^"]*)" to the Organization "([^"]*)"')
def assign_org_to_user(step, username, name):
    """ Assign user to organization via the User admin """
    organization = Organization.objects.get(organizationtranslation__name=name)
    world.browser.visit(django_url('/admin/auth/user/'))
    world.browser.click_link_by_text(username)
    world.browser.select('organizations', organization.pk)
    world.browser.find_by_name('_save').first.click()

@step(r'"([^"]*)" is listed in the contributors list for Organization "([^"]*)" on its detail page')
def has_member(step, username, name):
    user = User.objects.get(username=username)
    world.browser.visit(django_url('/organizations/%s' % world.organization.organization_id))
    world.assert_text_present("Organization Contributors")
    world.assert_text_present(format_user_name(user))

@step(u'Then "([^"]*)" is selected on the "([^"]*)" User admin page')
def listed_in_user_admin(step, name, username):
    world.browser.visit(django_url('/admin/auth/user/'))
    world.browser.click_link_by_text(username)
    for member_elem in world.browser.find_by_css('#id_organizations option'):
        if member_elem.text == name:
            if member_elem.checked:
                break
    else:
        assert False, "%s not found in member list" % username

    assert True

@step(u'Given an admin removes "([^"]*)" from the Organization "([^"]*)"')
def remove_user_from_org(step, username, name):
    """ Remove user from organization via the Organization admin """
    user = User.objects.get(username=username)
    world.browser.find_by_xpath("//*[contains(@class, 'dynamic-organizationmembership_set')]//option[@value='%d']/../../../..//input[@type='checkbox']" % (user.id)).first.check()
    world.browser.find_by_name('_save').first.click()

#@step(u'Given an admin removes "([^"]*)" from the Organization "([^"]*)"')
#def remove_org_from_user(step, username, name):
#    """ Remove user from organization via the User admin """
#    world.browser.visit(django_url('/admin/auth/user/'))
#    world.browser.click_link_by_text(username)
#    for member_elem in world.browser.find_by_css('#id_organizations option'):
#        if member_elem.text == name:
#            member_elem.click()
#    world.browser.find_by_name('_save').first.click()

@step(u'Then "([^"]*)" is not listed in the contributors list for Organization "([^"]*)"')
def not_member(step, username, name):
    user = User.objects.get(username=username)
    world.browser.visit(django_url('/organizations/%s' % world.organization.organization_id))
    world.assert_text_not_present("Organization Contributors")
    world.assert_text_not_present(format_user_name(user))

@step(u'Then "([^"]*)" is not selected on the "([^"]*)" User admin page')
def not_listed_in_user_admin(step, name, username):
    world.browser.visit(django_url('/admin/auth/user/'))
    world.browser.click_link_by_text(username)
    for member_elem in world.browser.find_by_css('#id_organizations option'):
        if member_elem.text == name:
            if member_elem.checked:
                break
    else:
        return True

    assert False, "%s found in member list" % username

@step(u'Given the User "([^"]*)" is associated with the Organization "([^"]*)"')
def add_user_to_org(step, username, org_name):
    user = User.objects.get(username=username)
    org = Organization.objects.get(organizationtranslation__name=org_name)
    try:
        Organization.members.through.objects.get(user=user, organization=org)
    except Organization.members.through.DoesNotExist:
        Organization.members.through.objects.create(user=user, organization=org)

@step(u'Given the user navigates to the Organization\'s detail page')
def visit_detail_page(step):
    world.browser.visit(django_url('/organizations/%s' % world.organization.organization_id))


@step(u'Then the Organization\'s name is listed as "([^"]*)"')
def see_name(step, name):
    world.assert_text_present(name)

# HACK: I couldn't figure out how to write a regex that would match
# "created|last edited", so I just wrote to different step definitions and
# use this function to do the heavy lifting
def assert_organization_date_now(name, date_type):
    org = Organization.objects.get(organizationtranslation__name=name)
    if date_type == "created":
        date = getattr(org, 'created')
    elif date_type == "last edited":
        date = getattr(org, 'last_edited')
    else:
        assert False
    world.assert_now(date, 60)

@step(u'Then the "([^"]*)" Organization\'s last edited field should be set to within 1 minute of the current date and time')
def organization_edited_now(step, name):
    assert_organization_date_now(name, "last edited")

@step(u'Then the "([^"]*)" Organization\'s created field should be set to within 1 minute of the current date and time')
def organization_created_now(step, name):
    assert_organization_date_now(name, "created")
