"""Template tags to display customizations to Django CMS"""
from django import template
from cms.templatetags.cms_tags import PageAttribute
from cmsplugin_storybase.settings import STORYBASE_MEGAMENU_ITEMS

register = template.Library()

MEGAMENU_ITEMS = dict([(item, None) if not isinstance(item, (list, tuple))
                       else item for item in STORYBASE_MEGAMENU_ITEMS])

def _filter_menu_items(children, allowed_ids=None):
    filtered = []
    for child in children:
        try:
            menu_id = child.attr['reverse_id']
        except KeyError:
            menu_id = child.id

        if menu_id in allowed_ids:
            filtered.append(child)
    return filtered

def filter_menu_items(value, arg):
    allowed_ids = arg.split(",")
    return _filter_menu_items(value, allowed_ids)
register.filter("filtermenuitems", filter_menu_items)

def megamenu_items(value):
    """Filter a list of menu items to only those shown in the megamenu"""
    return _filter_menu_items(value, MEGAMENU_ITEMS)
register.filter("megamenuitems", megamenu_items)

def megamenu_template(value):
    return MEGAMENU_ITEMS[value]
register.filter("megamenutemplate", megamenu_template)
