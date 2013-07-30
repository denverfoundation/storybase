from django.conf import settings

STORYBASE_UNPUBLISHED_STORY_NOTIFICATION_DELAY = getattr(settings,
    'STORYBASE_UNPUBLISHED_STORY_NOTIFICATION_DELAY', 5)
"""
Number days from the current time to schedule the sending of unpublished
story notifications

Default is 5

"""
