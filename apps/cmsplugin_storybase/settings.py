"""Settings for StoryBase/Django CMS integration"""

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

__all__ = ["STORYBASE_EXPLORE_MENU_POSITION"]

STORYBASE_BUILD_MENU_POSITION = getattr(settings,
    'STORYBASE_BUILD_MENU_POSITION', 0)
"""
Zero-indexed position where the "Build ..." menu should be inserted

Setting this to 0 would make this menu the first item in the menu
"""

STORYBASE_EXPLORE_MENU_POSITION = getattr(settings,
    'STORYBASE_EXPLORE_MENU_POSITION', 3)
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

STORYBASE_MEGAMENU_ITEMS = getattr(
    settings, 'STORYBASE_MEGAMENU_ITEMS',
    ['home', 'story-builder-landing', 'explore', 'learn', 'news', 'about'])
"""
CMS Page Reverse IDs or menu entry menu IDs of items that should appear in
the megamenu at the top of most pages

Each item can be a string, or a length=2 tuple of
('id', 'path/to/megamenu_template_to_use.html').
"""


