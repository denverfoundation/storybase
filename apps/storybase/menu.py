"""
(More) DRY menus used across storybase
"""
from django.core.urlresolvers import reverse, resolve
from django.http import Http404

class MenuRegistry(object):
    """
    Central registry of menus.

    This is not meant to be instantiated in calling code. Instead use the
    instance ``storybase.menu.registry``

    """
    _menus = {}

    def register(self, menu):
        """Register a menu instance"""
        self._menus[menu.menu_id] = menu

    def get(self, menu_id):
        """
        Get a menu instance from the registry.

        Arguments:
        menu_id -- Identifier of menu instance used when the menu was
                   constructed

        """
        return self._menus[menu_id]


class Menu(object):
    """Navigation menu"""
    _items = []

    def __init__(self, menu_id, label, **kwargs):
        """
        Constructor

        Arguments:
        menu_id -- String uniquely identifying this menu. This will be used
                   for retrieving the menu from the registry
        label -- String representing the title or heading for the menu

        """
        self.menu_id = menu_id
        self.label = label

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def add_url(self, url_name, label, tooltip=""):
        """
        Add an item to the menu

        Arguments:
        url_name -- Name for URL pattern as set in the Django project's URL
                    configuration
        label -- Text that will be used when displaying the menu item
        tooltop -- Text that will be shown as the tooltio when displaying
                   the menu item. Defaults to an empty string.

        """
        self._items.append({
            'url_name': url_name,
            'label': label,
            'tooltip': tooltip,
        })

    def get_items(self, active_path=None):
        """
        Returns a list of menu items as dictionary objects.

        Arguments:
        active_path: URL path to be considered active. It will be used
                     to select the active menu item in the list of returned
                     items. Default None.

        Returns the menu items in the order in which they were added to the
        menu by ``add_url``.

        Each menu item dictionary has the following keys:

        * url -- URL path for the menu item
        * label -- Text for the menu item
        * tooltip -- Extended description of the menu item
        * active -- Is the menu item the one for the active view?

        """
        items = []
        for item in self._items:
            normalized_item = {
                'label': item['label'],
                'tooltip': item['tooltip'],
                'url': reverse(item['url_name']),
                'active': False,
            }
            if active_path:
                try:
                    match = resolve(active_path)
                    if match.url_name == item['url_name']:
                        normalized_item['active'] = True
                except Http404:
                    # Couldn't resolve active path
                    pass
                           
            items.append(normalized_item)

        return items

registry = MenuRegistry()
