"""Settings for StoryBase/Django CMS integration"""

from django.conf import settings
from django.utils.translation import ugettext as _

__all__ = ["STORYBASE_EXPLORE_MENU_POSITION"]

STORYBASE_BUILD_MENU_POSITION = getattr(settings, 
    'STORYBASE_BUILD_MENU_POSITION', 0)
"""
Zero-indexed position where the "Build ..." menu should be inserted

Setting this to 0 would make this menu the first item in the menu 
"""

STORYBASE_EXPLORE_MENU_POSITION = getattr(settings, 
    'STORYBASE_EXPLORE_MENU_POSITION', 1)
"""
Zero-indexed position where the "Explore ..." menu should be inserted

Setting this to 0 would make this menu the first item in the menu 
"""

STORYBASE_BUILD_TITLE = getattr(
    settings, 'STORYBASE_BUILD_TITLE', _("Build a Story"))
"""
The title of the story builder view

This will appear in the menus and on the page itself
"""

STORYBASE_EXPLORE_TITLE = getattr(
    settings, 'STORYBASE_EXPLORE_TITLE', _("Explore"))
"""
The title of the story exploration view

This will appear in the menus and on the page itself
"""


STORYBASE_ORGANIZATION_LIST_TITLE = getattr(
    settings, 'STORYBASE_ORGANIZATION_LIST_TITLE', _("Organizations"))
"""
The title of the organization list view

This will appear in the menus and on the page itself
"""

STORYBASE_PROJECT_LIST_TITLE = getattr(
    settings, 'STORYBASE_PROJECT_LIST_TITLE', _("Projects"))
"""
The title of the project list view

This will appear in the menus and on the page itself
"""

