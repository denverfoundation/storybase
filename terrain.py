from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection
from django.db.utils import DatabaseError
from django.test.utils import setup_test_environment, teardown_test_environment
from lettuce import before, after, world
from south.management.commands import patch_for_test_db_setup
from splinter.browser import Browser

@world.absorb
def create_admin_user():
    """ Create an admin user """
    world.admin_username = 'admin'
    world.admin_email = 'admin@localhost.localdomain'
    world.admin_password = 'admin'
    user = User.objects.create_user(world.admin_username, world.admin_email,
        world.admin_password)
    user.is_staff = True
    user.is_superuser = True
    user.save()

# TODO: Figure out why database create with create_test_db doesn't 
# allow writing.
#@before.runserver
def setup_database(server):
    """ Create a test database and initialize the test environment """
    world.old_db_name = settings.DATABASES['default']['NAME']
    # Force running migrations after syncdb.
    # syncdb gets run automatically by create_test_db(), and
    # South's syncdb (that runs migrations after the default
    # syncdb) normally gets called in a test environment, but
    # apparently not when calling create_test_db(). 
    # So, we have to use this monkey patched version.
    patch_for_test_db_setup()
    connection.creation.create_test_db(verbosity=5)
    setup_test_environment()

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

@before.each_scenario
def reset_data(scenario):
    """ Clean up Django """
    call_command('flush', interactive=False, verbosity=0)

@after.all
def teardown(total):
    """ Tear down the test database and tear down the test environment """
    #connection.creation.destroy_test_db(world.old_db_name)
    teardown_test_environment()

@after.all
def teardown_browser(total):
    world.browser.quit()
