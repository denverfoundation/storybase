"""Utility functions for dealing with users and groups of users"""

import re

from django.contrib.auth.models import User

import storybase_user.models
from storybase_user.models import Organization, Project, ADMIN_GROUP_NAME

def get_admin_emails():
    """Get a list of admin email addresses"""
    admin_qs = User.objects.filter(groups__name=ADMIN_GROUP_NAME)
                               
    if not admin_qs.count():
        # No CA admin users, default to superusers
        admin_qs = User.objects.filter(is_superuser=True)

    return admin_qs.values_list('email', flat=True)

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

def split_name(full_name):
    """Split a full name into first and last names"""
    first_name = ""
    last_name = ""
    # Split the name along whitespace
    name_chunks = re.split(r'\s+', full_name)
    if len(name_chunks):
        if len(name_chunks) >= 2:
            first_name = ' '.join(name_chunks[:-1])
            last_name = name_chunks[-1]
        else:
            # Only one part of the name, set the first name
            first_name = name_chunks[0]

    return (first_name, last_name)

