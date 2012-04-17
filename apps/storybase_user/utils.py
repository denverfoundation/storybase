"""Utility functions for dealing with users and groups of users"""

from django.contrib.auth.models import User

from storybase_user.models import ADMIN_GROUP_NAME

def get_admin_emails():
    """Get a list of admin email addresses"""
    admin_qs = User.objects.filter(groups__name=ADMIN_GROUP_NAME)
                               
    if not admin_qs.count():
        # No CA admin users, default to superusers
        admin_qs = User.objects.filter(is_superuser=True)

    return admin_qs.values_list('email', flat=True)
