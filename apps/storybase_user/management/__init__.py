from django.contrib.auth.models import User
from django.db.models.signals import post_syncdb

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
