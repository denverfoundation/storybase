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
from storybase_user.models import Organization


@world.absorb
def create_organization(name):
    """ Create an Organization """
    Organization.objects.create(name=name)

@world.absorb
def admin_login():
    """ Log in to the Django admin """
    world.browser.visit(django_url('/admin'))
    world.browser.fill('username', world.admin_username)
    world.browser.fill('password', world.admin_password)
    button = world.browser.find_by_css('.submit-row input').first
    button.click()

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
@step(u'Given an admin creates the User "([^"]*)"')
def create_user(step, username):
    new_user = User.objects.create_user(username, username + '@fakedomain.com', 'password')

@step(u'Given the User "([^"]*)" exists')
def user_exists(step, username):
    User.objects.get(username=username)
