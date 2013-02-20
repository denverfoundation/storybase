from django.core.urlresolvers import reverse, resolve
from django.http import Http404

class MenuRegistry(object):
    _menus = {}

    def register(self, menu):
        self._menus[menu.menu_id] = menu

    def get(self, menu_id):
        return self._menus[menu_id]


class Menu(object):
    _items = []

    def __init__(self, menu_id, label, **kwargs):
        self.menu_id = menu_id
        self.label = label

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def add_url(self, url_name, label, tooltip=""):
        self._items.append({
            'url_name': url_name,
            'label': label,
            'tooltip': tooltip,
        })

    def get_items(self, active_path=None):
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
