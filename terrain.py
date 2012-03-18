import re
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection
from django.db.utils import DatabaseError
from django.test.utils import setup_test_environment, teardown_test_environment
from lettuce import before, after, step, world
from lettuce.django import django_url
#from south.management.commands import patch_for_test_db_setup
from splinter.browser import Browser
from splinter.exceptions import ElementDoesNotExist
import storybase_user
from storybase_user.models import Organization, OrganizationTranslation

# Utility methods

@world.absorb
def create_organization(name):
    """ Create an Organization """
    org = Organization()
    org.save()
    org_translation = OrganizationTranslation(name=name, organization=org)
    org_translation.save()

@world.absorb
def set_changed(model, field):
    """ Mark a field of a Model instance as changed
    
    The changed fields are ignored when checking that the model instance
    fields are the same pre/post editing the instance.

    Arguments:
    model -- Model class name, e.g. "Project"
    field -- Field name, e.g. "name"

    """
    try:
        changed = getattr(world, "%s_changed" % model.lower())
        changed.append(field)
    except AttributeError:
        pass

def _class_lookup(model):
    """ Get a "fully qualified" class object for a model

    Arguments
    model -- Model class name as a string, e.g. "Project"

    """
    classes = {
        'Organization': storybase_user.models.Organization,
        'Project': storybase_user.models.Project
    }
    return classes[model]

@world.absorb
def save_info(model, instance_id):
    """ Save a model instance's info for later comparison
    
    Assumes that world.browser is on a Model instance's admin  edit page
    
    Arguments:
    model -- Class name of the model instance, e.g. "Project"
    instance_id -- UUID ID attribute of the model instance
    
    """
    klass = _class_lookup(model) 
    model_lower = model.lower()
    setattr(world, model_lower, 
            klass.objects.get(**{"%s_id" % model_lower: instance_id}))
    setattr(world, "%s_changed" % model_lower, [])

# Custom Assertions

@world.absorb
def assert_is_uuid4(s):
    """ Check whether a string is a UUID4 """
    assert re.match(r'^[0-9a-f]{32,32}$', s) is not None

@world.absorb
def assert_text_present(s):
    assert world.browser.is_text_present(s)

@world.absorb
def assert_text_not_present(s):
    assert world.browser.is_text_not_present(s)

@world.absorb
def assert_today(dt):
    today = datetime.today()
    assert dt.year == today.year
    assert dt.month == today.month
    assert dt.day == today.day

@world.absorb
def assert_now(dt, allowance=0):
    """ Test whether a datetime object is equivalent to the current date/time 
    
    Arguments:
    dt -- datetime object
    allowance -- seconds of difference allowed while still considering times equal

    """
    now = datetime.now()
    delta = now - dt
    assert delta.seconds <= allowance 

@world.absorb
def assert_text_in_list(selector, text):
    """ Check whether the text appears in a list's items
    
    Arguments:
    selector -- CSS selector for list item elements
    text -- Text to search for in selected list items
    """
    for member_elem in world.browser.find_by_css(selector):
        if member_elem.text == text:
            break
    else:
        assert False, "%s not found in list" % text

    assert True

@world.absorb
def assert_text_not_in_list(selector, text):
    """ Check whether the text doesn't appears in a list's items
    
    Arguments:
    selector -- CSS selector for list item elements
    text -- Text to search for in selected list items
    """
    for member_elem in world.browser.find_by_css(selector):
        if member_elem.text == text:
            break
    else:
        return True

    assert False, "%s found in list" % text

# TODO: Figure out why database create with create_test_db doesn't 
# allow writing.
#@before.runserver
#def setup_database(server):
#    """ Create a test database and initialize the test environment """
#    world.old_db_name = settings.DATABASES['default']['NAME']
#    # Force running migrations after syncdb.
#    # syncdb gets run automatically by create_test_db(), and
#    # South's syncdb (that runs migrations after the default
#    # syncdb) normally gets called in a test environment, but
#    # apparently not when calling create_test_db(). 
#    # So, we have to use this monkey patched version.
#    patch_for_test_db_setup()
#    connection.creation.create_test_db(verbosity=5)
#    setup_test_environment()

@before.harvest
def initialize_database(server):
    call_command('syncdb', interactive=False, verbosity=0)
    try:
        call_command('migrate', interactive=False, verbosity=0)
    except DatabaseError as e:
        # HACK: Workaround for weird Django-CMS migration that tries
        # to re-run.
        if str(e).strip() == 'relation "cms_cmsplugin" already exists':
            pass
        else:
            raise
    call_command('flush', interactive=False, verbosity=0)
    call_command('loaddata', 'all', verbosity=0)
    setup_test_environment()

@before.runserver
def setup_browser(server):
    world.browser = Browser('webdriver.firefox')

@before.each_feature
def reset_data(feature):
    """ Clean up Django """
    call_command('flush', interactive=False, verbosity=0)

@before.each_feature
def create_admin_user(feature):
    """ Create an admin user """
    world.admin_username = 'admin'
    world.admin_email = 'admin@localhost.localdomain'
    world.admin_password = 'admin'
    world.admin_user = User.objects.create_user(world.admin_username, world.admin_email,
        world.admin_password)
    world.admin_user.is_staff = True
    world.admin_user.is_superuser = True
    world.admin_user.save()

@after.all
def debug(total):
    if hasattr(world, 'html'):
        print world.html

@after.all
def teardown(total):
    """ Tear down the test database and tear down the test environment """
    #connection.creation.destroy_test_db(world.old_db_name)
    teardown_test_environment()

@after.all
def teardown_browser(total):
    """ Close the test browser 

    Leaves the browser open if tests failed as it may be helpful in debugging
    """
    if total.scenarios_passed == total.scenarios_ran:
        world.browser.quit()

# Global steps used throughout tests
@step(u'Given the admin user is logged in')
def admin_login(step):
    """ Log in to the Django admin """
    world.browser.visit(django_url('/admin'))
    if world.browser.is_text_present('Username:') and world.browser.is_text_present('Password:'):
        world.browser.fill('username', world.admin_username)
        world.browser.fill('password', world.admin_password)
        button = world.browser.find_by_css('.submit-row input').first
        button.click()

@step(u'Given an admin creates the User "([^"]*)"')
def create_user(step, username):
    new_user = User.objects.create_user(username, username + '@fakedomain.com', 'password')

@step(u'Given the User "([^"]*)" exists')
def user_exists(step, username):
    User.objects.get(username=username)

@step(u'Given the user navigates to the "([^"]*)" admin')
def visit_model_admin(step, model_name):
    world.browser.visit(django_url('/admin'))
    world.browser.click_link_by_text(model_name)

@step(u'Given the user navigates to the "([^"]*)" addition page')
def visit_model_add_admin(step, model_name):
    step.given("Given the user navigates to the \"%s\" admin" % model_name)
    world.browser.click_link_by_href("add/")

@step(u'Given the user sets the name of the "([^"]*)" to "([^"]*)"')
def edit_name(step, model, name):
    try:
        world.browser.fill('name', name)
    except ElementDoesNotExist:
        translated_field_name = "%stranslation_set-0-name" % model.lower()
        world.browser.fill(translated_field_name, name) 
    world.set_changed(model, 'name')

@step(u'Given the user edits the description of the "([^"]*)" to be "([^"]*)"')
def edit_description(step, model, description):
    try:
        world.browser.fill('description', description)
    except ElementDoesNotExist:
        translated_field_name = "%stranslation_set-0-description" % model.lower()
        world.browser.fill(translated_field_name, description) 
    world.set_changed(model, 'description')

@step(u'Given the user edits the description of the "([^"]*)" to be the following:')
def edit_description_long(step, model):
    try:
        world.browser.fill('description', step.multiline)
    except ElementDoesNotExist:
        translated_field_name = "%stranslation_set-0-description" % model.lower()
        world.browser.fill(translated_field_name, step.multiline) 

    world.set_changed(model, 'description')

@step(u'Given the user sets the website URL of the "([^"]*)" to "([^"]*)"')
def edit_website_url(step, model, website_url):
    try:
        world.browser.fill('website_url', website_url)
    except ElementDoesNotExist:
        translated_field_name = "%stranslation_set-0-website_url" % model.lower()
        world.browser.fill(translated_field_name, website_url) 
    world.set_changed(model, 'website_url')
