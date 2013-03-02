from django.utils.translation import ugettext_lazy as _
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from cmsplugin_storybase.menu import NewsItemMenu

class NewsItemApphook(CMSApp):
    """Apphook to attach list and detail views of news items to a CMS page"""
    name = _("NewsItem Apphook")
    urls = ["cmsplugin_storybase.news_urls"]
    menus = [NewsItemMenu]

apphook_pool.register(NewsItemApphook)
