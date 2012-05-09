"""Settings for StoryBase/Django CMS integration"""

from django.conf import settings

__all__ = ["STORYBASE_EXPLORE_MENU_POSITION"]

STORYBASE_EXPLORE_MENU_POSITION = getattr(settings, 
                                          'STORYBASE_EXPLORE_MENU_POSITION', 0)
"""
Zero-indexed position where the "Explore ..." menu should be inserted

Setting this to 0 would make this menu the first item in the menu 
"""
