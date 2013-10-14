"""Custom endpoints that don't really make sense as Tastypie Resources"""
import urllib2
import socket
from lxml import etree
import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError
from django.views.generic import View

class ProxyView(View):
    """View that fetches a remote URL and passes on the response"""
    endpoint = None

    def get_endpoint(self):
        """
        Returns the remote endpoint URL
        
        Defaults to the ``endpoint``.
        """
        return self.endpoint

    def get_remote_response(self, url, request):
        """
        Make a request to the remote endpoint and returns the response
        """
        req = urllib2.Request("%s?%s" % (url, request.META['QUERY_STRING']))
        return urllib2.urlopen(req)

    def create_response(self, resp):
        """
        Returns an ``HttpResonse`` object based on the remote endpoint response

        By default, pass through the response body and content type. If you
        want to alter the response, override this method.
        """
        info = resp.info()
        return self.response_class(resp.read(), content_type=info.get('Content-Type'))

    def proxy_request(self, url, request):
        """
        Makes a request to a remote endpoint and returns an ``HttpResponse``
        """
        resp = self.get_remote_response(url, request)
        return self.create_response(resp)

    def get(self, request, *args, **kwargs):
        endpoint = self.get_endpoint()
        try:
            return self.proxy_request(endpoint, request)
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

    Converts the data from XML to JSON. The conversion is needed because it's
    somewhat painful to parse HTML from within XML data and append the HTML
    to the DOM on the client side.

    Ignores all data from the remote endpoint except for the HTML representation
    of the license.
    
    """
    http_method_names = ['get']
    response_class = HttpResponse

    def get_endpoint(self):
        return getattr(settings, 'CC_LICENSE_GET_ENDPOINT', 
            'http://api.creativecommons.org/rest/1.5/license/standard/get')

    def create_response(self, resp):
        root = etree.fromstring(resp.read());
        # Get the contents of the '<html>' element of the XML document
        resp_data = {
            'html': ''.join([etree.tostring(child) for child in root.find('html')]),
        }
        return self.response_class(json.dumps(resp_data),
            content_type="application/json")
