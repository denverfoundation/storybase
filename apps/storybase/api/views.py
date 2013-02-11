"""Custom endpoints that don't really make sense as Tastypie Resources"""
import urllib2
import socket

from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError
from django.views.generic import View

class ProxyView(View):
    """View that fetches a remote URL and passes on the response"""
    endpoint = None

    def get_endpoint(self):
        return self.endpoint

    def get(self, request, *args, **kwargs):
        endpoint = self.get_endpoint()
        req = urllib2.Request("%s?%s" % (endpoint, request.META['QUERY_STRING']))
        try:
            resp = urllib2.urlopen(req)
            info = resp.info()
            return self.response_class(resp.read(), content_type=info.get('Content-Type'))
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                if isinstance(e.reason, socket.timeout):
                    return HttpResponseServerError("Request to %s timed out" % (endpoint)) 

                return HttpResponseServerError("Failed to retrieve %s. Reason: %s" % (endpoint, e.reason))
            elif hasattr(e, 'code'):
                return HttpResponseServerError("The server couldn't fulfill the request for %s. Reason: %s" % (endpoint, e.code))
            else:
                raise

class CreativeCommonsLicenseGetProxyView(ProxyView):
    """
    Proxy for the Creative Commons API /license/<class>/get? endpoint

    See http://api.creativecommons.org/docs/readme_15.html
    
    """
    http_method_names = ['get']
    response_class = HttpResponse

    def get_endpoint(self):
        return getattr(settings, 'CC_LICENSE_GET_ENDPOINT', 
            'http://api.creativecommons.org/rest/1.5/license/standard/get')
