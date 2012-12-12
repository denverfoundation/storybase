"""Utility functions for dealing with users and groups of users"""

import hashlib
import urllib

from django.contrib.auth.models import User
from django.core.mail import send_mail

import storybase_user.models
from storybase_user.models import Organization, Project, ADMIN_GROUP_NAME

def is_admin(user):
    from django.db.models import Q
    return user in User.objects.filter(
        Q(groups__name=ADMIN_GROUP_NAME) | Q(is_superuser=True)
    )

def get_admin_emails():
    """Get a list of admin email addresses"""
    admin_qs = User.objects.filter(groups__name=ADMIN_GROUP_NAME)
                               
    if not admin_qs.count():
        # No CA admin users, default to superusers
        admin_qs = User.objects.filter(is_superuser=True)

    return admin_qs.values_list('email', flat=True)


def send_admin_mail(subject, message, from_email, **kwargs):
    """Wrapper for send_mail that sends email to all admins"""
    admin_emails = get_admin_emails()
    if admin_emails:
        send_mail(subject, message, from_email, admin_emails, **kwargs)


def bulk_create(model, hashes, name_field='name',
                description_field='description'):
    create_fn = getattr(storybase_user.models,
                        "create_%s" % model.__name__.lower())
    for obj_dict in hashes:
        name = obj_dict[name_field]
        description = obj_dict[description_field]
        create_fn(name=name, description=description)


def bulk_create_organization(hashes, name_field='name',
                             description_field='description'):
    bulk_create(Organization, hashes, name_field, description_field)


def bulk_create_project(hashes, name_field='name',
                        description_field='description'):
    bulk_create(Project, hashes, name_field, description_field)

def format_user_name(user):
    """Return the user's first name and last initial""" 
    user_name = "" 
    if user.is_active and user.first_name:
        user_name = user.first_name 
                            
        if user.last_name:
            user_name = "%s %s." % (user.first_name, user.last_name[0])
        else:
            user_name = user.first_name

    return user_name

def gravatar_url(email, default=None, size=40):
    """Retrieve a gravatar URL for a given e-mail address"""
    base_url = "http://www.gravatar.com/avatar/"
    options = {
        's': str(size),
    }
    if default:
        options['d'] = default
    url = base_url + hashlib.md5(email.lower()).hexdigest()
    url = url + "?" + urllib.urlencode(options)
    return url
