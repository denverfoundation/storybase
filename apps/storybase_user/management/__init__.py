from django.conf import settings
from django.contrib.auth import models as auth_app
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, post_syncdb

import storybase_user as user_app

# Based on django-email-usernames by Hakan Waara
# https://bitbucket.org/hakanw/django-email-usernames
def increase_username_and_email_length(sender, app, created_models, verbosity,
                                       interactive, **kwargs):
    """Signal handler to increase User field length on syncdb"""
    from django.core.management import call_command

    if (interactive and app.__name__ == 'django.contrib.auth.models' and
            User not in created_models):
        msg = ("\nYou have installed Django's auth system.  You can increase "
               " the length of the username and email address fields to 254 "
               " characters. If you don't do this, user registration may "
               " not work properly for users with long email addresses "
               "\nIncrease field length now? (yes/no): ")
        confirm = raw_input(msg)
        while 1:
            if confirm not in ('yes', 'no'):
                confirm = raw_input('Please enter either "yes" or "no": ')
                continue
            if confirm == 'yes':
                call_command("incuserfieldlen", interactive=True)
            break

post_syncdb.connect(increase_username_and_email_length)


def create_admin_group(sender, app, created_models, verbosity, interactive,
                       **kwargs):
    if (interactive and app.__name__ == 'django.contrib.auth.models' and
        Group not in created_models):
        try:
            admin_group = Group.objects.get(name=settings.ADMIN_GROUP_NAME)
        except Group.DoesNotExist:
            msg = ("\nCreate administrator group? (yes/no): ")
            confirm = raw_input(msg)
            while 1:
                if confirm not in ('yes', 'no'):
                    confirm = raw_input('Please enter either "yes" or "no": ')
                    continue
                if confirm == 'yes':
                    Group.objects.create(name=settings.ADMIN_GROUP_NAME)    
                break
post_syncdb.connect(create_admin_group)

def create_superuser(sender, app, **kwargs):
    """
    Custom version of the create_superuser signal handler
    
    This version connects to South's post_migrate signal instead of
    post_syncd
    """
    from django.core.management import call_command

    # Only prompt to create a user this after migrations for the user app
    # have run and if there are really no users.
    if (app == 'storybase_user' and kwargs.get('interactive', True) and
            User.objects.filter(is_superuser=True).count() == 0):
        msg = ("\nYou just installed Django's auth system, which means you "
            "don't have any superusers defined.\nWould you like to create one "
            "now? (yes/no): ")
        confirm = raw_input(msg)
        while 1:
            if confirm not in ('yes', 'no'):
                confirm = raw_input('Please enter either "yes" or "no": ')
                continue
            if confirm == 'yes':
                call_command("createsuperuser", interactive=True)
            break
