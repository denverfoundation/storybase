import re
from exceptions import UrlNotMatched

class EmbedableResource(object):
    resource_providers = []

    @classmethod
    def register(cls, provider_cls):
        cls.resource_providers.append(provider_cls)

    @classmethod
    def get_html(cls, url):
        for provider_cls in cls.resource_providers:
            provider = provider_cls()
            try:
                return provider.get_html(url)
            except UrlNotMatched:
                pass

        raise UrlNotMatched

class EmbedableResourceProvider(object):
    url_pattern = r''

    def match(self, url):
        return re.match(self.url_pattern, url) is not None

    def get_html(self, url):
        raise UrlNotMatched


class GoogleSpreadsheetProvider(EmbedableResourceProvider):
    url_pattern = r'^https://docs.google.com/spreadsheet/pub\?key=[0-9a-zA-Z]+'
    def get_html(self, url, width=500, height=300):
        if not self.match(url):
            raise UrlNotMatched

        return "<iframe width='500' height='300' frameborder='0' src='%s&widget=true'></iframe>" % url


class GoogleMapProvider(EmbedableResourceProvider):
    def get_html(self, url, width=425, height=350):
        if not self.match(url):
            raise UrlNotMatched

        return '<iframe width="%d" height="%d" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="%s&amp;output=embed"></iframe><br /><small><a href="%s&amp;source=embed" style="color:#0000FF;text-align:left">View Larger Map</a></small>' % (width, height, url, url)

EmbedableResource.register(GoogleSpreadsheetProvider)
EmbedableResource.register(GoogleMapProvider)
