from django.contrib.auth.models import Group, User
from lettuce import step, world
from lettuce.django import django_url
from splinter.exceptions import ElementDoesNotExist

@step(u'Given an admin user assigns "([^"]*)" user to the "([^"]*)" group')
def assign_user_to_group(step, username, group_name):
    world.create_admin_user()
    group = Group.objects.create(name=group_name) 
    group.save()
    new_user = User.objects.create_user(username, username + '@fakedomain.com', 'password')

    world.browser.visit(django_url('/admin'))
    world.browser.fill('username', world.admin_username)
    world.browser.fill('password', world.admin_password)
    button = world.browser.find_by_css('.submit-row input').first
    button.click()
    world.browser.click_link_by_text("Users")
    try:
        world.browser.click_link_by_text(username)
    except ElementDoesNotExist:
        world.html = world.browser.html
        raise

    world.browser.check('is_staff')
    world.browser.select('groups', '1')
    world.browser.find_by_name('_save').first.click()

@step(r'"(.*)" shows up in a listing of "(.*)" users')
def see_user_in_group(step, username, group_name):
    world.browser.click_link_by_text(group_name)
    assert world.browser.is_text_present(username)


@step(r'an admin user unassigns the user "([^"]*)" from the "([^"]*)" group')
def unassign_user_from_group(step, username, group_name):
    world.browser.visit(django_url('/admin'))
    world.browser.click_link_by_text("Users")
    world.browser.click_link_by_text(username)
    world.browser.select('groups', '1')
    world.browser.find_by_name('_save').first.click()

@step(r'"([^"]*)" doesn\'t show up in a listing of "([^"]*)" users')
def dont_see_user_in_group(step, username, group_name):
    world.browser.click_link_by_text(group_name)
    assert world.browser.is_text_not_present(username)
