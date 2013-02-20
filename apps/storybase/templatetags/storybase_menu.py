"""
Tag library for displaying menus
"""
from django.template import Library
from django.template.loader import render_to_string
from storybase.menu import registry as menu_registry

register = Library()

@register.simple_tag
def storybase_menu(menu_id, template_name, path=None):
    """
    Arguments:
    menu_id --- Unique identifier of a ``storybase.menu.Menu`` instance
    template_name -- Name of the template to be used to render the menu
    path -- Active path of the view

    """
    menu = menu_registry.get(menu_id)
    context = {
        'menu': menu,
        'menu_items': menu.get_items(path),
    }

    return render_to_string(template_name, context)
