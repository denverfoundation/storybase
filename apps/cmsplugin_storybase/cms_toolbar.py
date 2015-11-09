from django.core.urlresolvers import resolve, Resolver404
from django.utils.six.moves.urllib.parse import urlparse
from django.utils.translation import get_language_info, ugettext_lazy as _
from cms.extensions.toolbar import ExtensionToolbar
from cms.toolbar.items import ModalItem
from cms.toolbar_pool import toolbar_pool

from cmsplugin_storybase.models import TeaserExtension


@toolbar_pool.register
class TeaserExtensionToolbar(ExtensionToolbar):
    model = TeaserExtension

    def __init__(self, request, toolbar, is_current_app, app_path):
        super(TeaserExtensionToolbar, self).__init__(request, toolbar, is_current_app, app_path)
        self.extended_model = self.model.extended_object.field.rel.to

    def populate(self):
        current_page_menu = self._setup_extension_toolbar()
        if current_page_menu and self.toolbar.edit_mode:
            sub_menu = self._get_sub_menu(current_page_menu, 'submenu_label', 'Page Submenu', 0)
            urls = self.get_title_extension_admin()
            for title_extension, url in urls:
                try:
                    # Title extension exists. Get it from ResolverMatch
                    obj_id = int(resolve(url)[1][0])
                    title = self.model.objects.get(pk=obj_id).extended_object
                except Resolver404:
                    # Title extension does not exist. Look up related object from create url
                    query = urlparse(url)[4]
                    obj_id = int(query.split('=')[1])
                    title = self.extended_model.objects.get(pk=obj_id)

                item = ModalItem(_('%(lang)s Page Teaser' % {
                                     'lang': get_language_info(title.language)['name']
                                 }),
                                 url=url,
                                 disabled=not self.toolbar.edit_mode)

                position = 0
                for index, sub_menu_item in enumerate(sub_menu.items):
                    if item.name > sub_menu_item.name:
                        position = index
                    else:
                        break

                sub_menu.add_item(item, position=position)
