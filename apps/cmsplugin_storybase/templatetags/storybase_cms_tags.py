"""Template tags to display customizations to Django CMS"""
from django import template
from cms.templatetags.cms_tags import PageAttribute
from cmsplugin_storybase.settings import STORYBASE_MEGAMENU_ITEMS

register = template.Library()

# Patch the {% page_attribute %} tag to allow it to display the teaser
PageAttribute.valid_attributes = PageAttribute.valid_attributes + ["teaser",]

def megamenu_items(value, arg=None):
    """Filter a list of menu items to only those shown in the megamenu"""
    filtered = []
    if arg:
        allowed_ids = arg.split(",")
    else:
        allowed_ids = STORYBASE_MEGAMENU_ITEMS

    for child in value:
        try:
            menu_id = child.attr['reverse_id']
        except KeyError:
            menu_id = child.id

        if menu_id in allowed_ids:
            filtered.append(child)
    return filtered 
register.filter("megamenuitems", megamenu_items)
