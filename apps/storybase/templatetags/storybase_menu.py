from django.template import Library
from django.template.loader import render_to_string
from storybase.menu import registry as menu_registry

register = Library()

@register.simple_tag
def storybase_menu(menu_id, template_name, path=None):
    menu = menu_registry.get(menu_id)
    context = {
        'menu': menu,
        'menu_items': menu.get_items(path),
    }

    return render_to_string(template_name, context)
