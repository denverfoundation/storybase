from datetime import datetime
import re
#from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
#from django.db import connection
from django.db.utils import DatabaseError
from django.test.utils import setup_test_environment, teardown_test_environment
from lettuce import before, after, step, world
from lettuce.django import django_url
from nose.tools import assert_equal
#from south.management.commands import patch_for_test_db_setup
from splinter.browser import Browser
from splinter.exceptions import ElementDoesNotExist
import storybase_story
import storybase_user
from storybase_user.models import Organization, Project

# Utility methods

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
        'Project': storybase_user.models.Project,
        'Story': storybase_story.models.Story
    }
    return classes[model]

@world.absorb
def language_lookup(language):
    """ Convert a Python language code as a string

    There's probably a way to do this in the Python standard lib
    or through the Django API, but I was too lazy to search for it.

    """
    languages = {
        'Spanish': 'es',
        'English': 'en',
    }
    return languages[language]

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

@world.absorb
def find_translation_form(language, model):
    for translation_form in world.browser.find_by_css(".inline-related.dynamic-%stranslation_set" % model.lower()):
        language_select = translation_form.find_by_name("%s-language" % translation_form['id']).first
        if language_select.value == language_lookup(language):
            return translation_form

    raise ElementDoesNotExist 

@world.absorb
def translate_date(date_str, language):
    """ Cheap way of translating the internationalized version of the date

    This is Needed because the way we output Spanish dates doesn't 
    exactly match what a localized strptime expects.  For example,
    we still output times as HH:MM AM|PM as opposed to a 24-hour hour
    field.

    If we decide to use time formats that play nicer with a localized
    strptime, we could use setlocale and then parse with strptime.
    See http://stackoverflow.com/a/1299387/386210

    """
    if language == "Spanish":
        # Translate months from Spanish to English
        months_es = {
            'enero': 'January',
            'febrero': 'February',
            'marzo': 'March',
            'abril': 'April',
            'mayo': 'May',
            'junio': 'June',
            'julio': 'July',
            'agosto': 'August',
            'septiembre': 'September',
            'octubre': 'October',
            'noviembre': 'November',
            'diciembre': 'December'
        }
        for month_es in months_es.keys():
            if date_str.find(month_es) != -1:
                return date_str.replace(month_es, months_es[month_es])

    raise Exception 

@world.absorb
def format_field_name(field_name):
    """ Convert human-readable field name to machine field name

    E.g. website URL -> website_url

    """
    formatted_field_name = field_name.lower()
    formatted_field_name = re.sub(r'\s', '_', formatted_field_name)
    return formatted_field_name

@world.absorb
def select_option_by_text(name, text):
    """ Select an option from a select control based on the option's label """
    select = world.browser.find_by_name(name).first
    for option in select.find_by_tag('option'):
        if option.text == text:
            world.browser.select(name, option.value)
            return
    raise ElementDoesNotExist

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

@world.absorb
def assert_element_text_equal(selector, text):
    elem = world.browser.find_by_css(selector).first
    assert_equal(elem.text, text)

@world.absorb
def assert_list_equals(selector, list_items):
    """ Verify the text and order of items in a list """
    items = world.browser.find_by_css(selector)
    assert_equal(len(items), len(list_items))
    i = 0
    for item in items:
        assert_equal(item.text, list_items[i])
        i = i+1

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

@step(u'Given the user sets the "([^"]*)" of the "([^"]*)" to "([^"]*)"')
def edit_field(step, field_name, model, field_value):
    formatted_field_name = world.format_field_name(field_name)
    try:
        world.browser.fill(formatted_field_name, field_value)
    except ElementDoesNotExist:
        translated_field_name = "%stranslation_set-0-%s" % (model.lower(), formatted_field_name)
        world.browser.fill(translated_field_name, field_value) 
    world.set_changed(model, field_name)

@step(u'Given the user sets the "([^"]*)" of the "([^"]*)" to the following:')
def edit_field_long(step, field_name, model):
    formatted_field_name = world.format_field_name(field_name)
    try:
        world.browser.fill(formatted_field_name, step.multiline)
    except ElementDoesNotExist:
        translated_field_name = "%stranslation_set-0-%s" % (model.lower(), formatted_field_name)
        world.browser.fill(translated_field_name, step.multiline) 

    world.set_changed(model, formatted_field_name)

@step(u'Given the user adds a new "([^"]*)" "([^"]*)" translation')
def add_translation(step, language, model):
    translation_form = world.browser.find_by_css(".inline-related.dynamic-%stranslation_set" % model.lower()).last
    world.browser.select("%s-language" % translation_form['id'], language_lookup(language))

@step(u'Given the user sets the "([^"]*)" "([^"]*)" of the "([^"]*)" to "([^"]*)"')
def edit_translation_field(step, language, field_name, model, field_value):
    translation_form = world.find_translation_form(language, model)
    formatted_field_name = world.format_field_name(field_name)
    world.browser.fill("%s-%s" % (translation_form['id'], formatted_field_name), field_value)

@step(u'Given the user sets the "([^"]*)" "([^"]*)" of the "([^"]*)" to the following:')
def edit_translation_field_long(step, language, field_name, model):
    translation_form = world.find_translation_form(language, model)
    formatted_field_name = world.format_field_name(field_name)
    world.browser.fill("%s-%s" % (translation_form['id'], formatted_field_name), step.multiline)

@step(u'Given the user selects "([^"]*)" from the list of available organizations')
def select_org(step, org_name):
    org = Organization.objects.get(organizationtranslation__name=org_name)
    world.browser.select('organizations_old', org.pk)

@step(u'Given the user clicks the Add Organization icon')
def clicks_org_add_icon(step):
    world.browser.find_by_css('.organizations .selector-add').first.click()

@step(u'Given the user selects "([^"]*)" from the list of available Projects')
def select_project(step, project_name):
    project = Project.objects.get(projecttranslation__name=project_name)
    world.browser.select('projects_old', project.pk)

@step(u'Given the user clicks the Add Project icon')
def given_the_user_clicks_the_add_project_icon(step):
    world.browser.find_by_css('.projects .selector-add').first.click()

@step(u'Given the user clicks the save button')
def click_save(step):
    world.browser.find_by_name('_save').first.click()

@step(u'Given the user clicks the "([^"]*)" link')
def click_link(step, text):
    world.browser.click_link_by_text(text)
