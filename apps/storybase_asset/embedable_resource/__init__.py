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
    def get_html(self, url):
        if not self.match(url):
            raise UrlNotMatched

        return "<iframe width='500' height='300' frameborder='0' src='%s&widget=true'></iframe>" % url

EmbedableResource.register(GoogleSpreadsheetProvider)
