from lettuce import step, world
from lettuce.django import django_url
from splinter.exceptions import ElementDoesNotExist
from django.contrib.auth.models import Group, User

@step(u'Given an admin assigns "([^"]*)" user to the "([^"]*)" group$')
def assign_user_to_group(step, username, group_name):
    user = User.objects.get(username=username)
    group = Group.objects.get(name=group_name)
    try:
        User.groups.through.objects.get(user=user, group=group)
    except User.groups.through.DoesNotExist:
        user.groups.add(group)

@step(u'Given an admin assigns "([^"]*)" user to the "([^"]*)" group in the Django admin')
def assign_user_to_group_in_admin(step, username, group_name):
    world.browser.click_link_by_text("Users")
    try:
        world.browser.click_link_by_text(username)
    except ElementDoesNotExist:
        world.html = world.browser.html
        raise

    world.browser.check('is_staff')
    world.browser.select('groups', '1')
    world.browser.find_by_name('_save').first.click()

@step(r'"(.*)" shows up in a listing of "(.*)" users in the Django admin')
def see_user_in_group(step, username, group_name):
    world.browser.click_link_by_text(group_name)
    assert world.browser.is_text_present(username)

@step(r'an admin unassigns the user "([^"]*)" from the "([^"]*)" group in the Django admin')
def unassign_user_from_group(step, username, group_name):
    world.browser.visit(django_url('/admin'))
    world.browser.click_link_by_text("Users")
    world.browser.click_link_by_text(username)
    world.browser.select('groups', '1')
    world.browser.find_by_name('_save').first.click()

@step(r'"([^"]*)" doesn\'t show up in a listing of "([^"]*)" users in the Django admin')
def dont_see_user_in_group(step, username, group_name):
    world.browser.click_link_by_text(group_name)
    assert world.browser.is_text_not_present(username)
