from micawber.providers import Provider, ProviderRegistry

class MockProvider(Provider):
    """
    Mock Provider for resources that don't have an official oEmbed
    endpoint.

    In many cases, the embed code for the resource is consistent and
    we can construct it ourselves from the URL

    """
    def __init__(self, endpoint=None, **kwargs):
        # Don't require an endpoint parameter since it doesn't
        # really make sense for this use case
        super(MockProvider, self).__init__(endpoint, **kwargs)

class GoogleSpreadsheetProvider(MockProvider):
    url_pattern = r'^https://docs.google.com/spreadsheet/pub\?key=[0-9a-zA-Z]+'
    def request(self, url, **extra_params):
        width = extra_params.get('width', 500)
        height = extra_params.get('height', 300)
        return {
            'html': "<iframe width='%d' height='%d' frameborder='0' src='%s&widget=true'></iframe>" % (width, height, url),
            'type': "rich",
        }

class GoogleMapProvider(MockProvider):
    def request(self, url, **extra_params):
        width = extra_params.get('width', 425)
        height = extra_params.get('height', 350)
        return {
            'html': '<iframe width="%d" height="%d" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="%s&amp;output=embed"></iframe><br /><small><a href="%s&amp;source=embed" style="color:#0000FF;text-align:left">View Larger Map</a></small>' % (width, height, url, url),
            'type': "rich",
        }

def bootstrap_providers(cache=None):
    pr = ProviderRegistry(cache)
    pr.register('https?://\S*?flickr.com/\S*', Provider('http://www.flickr.com/services/oembed/'))
    # As of 2012-09-10, the default URLs provided by the "share"
    # button on a YouTube video use the youtu.be domain and no
    # "watch" parameter in the querystring, e.g. 
    # http://youtu.be/KpichyyCutw
    pr.register('https?://youtu.be/\S*', Provider('http://www.youtube.com/oembed'))
    # Also match non-shortened YouTube URls
    pr.register('https?://\S*.youtu(\.be|be\.com)/watch\S*', Provider('http://www.youtube.com/oembed'))
    pr.register('https?://soundcloud.com/\S*', Provider('http://soundcloud.com/oembed'))
    pr.register('https?://vimeo.com/\S*', Provider('http://vimeo.com/api/oembed.json'))
    pr.register('https?://www.slideshare.net/[^\/]+/\S*', Provider('http://www.slideshare.net/api/oembed/2'))
    pr.register('https?://instagr.am/\S*', Provider('http://api.instagram.com/oembed'))
    pr.register('https?://imgur.com\S*', Provider('http://api.imgur.com/oembed'))

    # Register our fake providers
    pr.register('https?://maps.google.com/maps.+', GoogleMapProvider(None))
    pr.register('https?://docs.google.com/spreadsheet/pub\?key=[0-9a-zA-Z]+', GoogleSpreadsheetProvider(None))
    return pr

