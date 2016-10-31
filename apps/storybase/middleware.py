import lxml.html

from django.conf import settings
from django.core.urlresolvers import is_valid_path, resolve
from django.http import HttpResponseRedirect
from django.middleware.locale import LocaleMiddleware as DjangoLocaleMiddleware
from django.shortcuts import render_to_response
from django.utils import translation
from django.utils.cache import patch_vary_headers


class MaintenanceModeMiddleware(object):
    """
    Middleware class to respond to all requests with a maintenance landing page
    """
    def process_request(self, request):
        try:
            match = resolve(request.path)
            if match.app_name is 'admin':
                return None
        except Exception as e:
            pass
        return render_to_response('maintenance.html')


class ExtractContentMiddleware(object):
    """
    Middleware class to return extracted HTML content from a response

    This is useful for breaking out content from a view response to be
    embedded in a popup or an iframe without the styling of layout
    scaffolding of a page.

    Pass extract=1 and a urlencoded CSS selector to return the contents of
    the first selected element in a bare HTML wrapper.

    Example:
    /path-to-view/?extract=1&selector=.intro

    Extracts the content in the first element with CSS class "intro"

    """
    def process_response(self, request, response):
        if 'extract' not in request.GET or 'selector' not in request.GET:
            return response

        selector = request.GET['selector']
        doc = lxml.html.fromstring(str(response))
        els = doc.cssselect(selector)
        if not len(els):
            return response

        el = els[0]
        context = {
            'content': lxml.html.tostring(el)
        }
        return render_to_response('storybase/extracted_content.html',
                                  context)


class LocaleMiddleware(DjangoLocaleMiddleware):
    """
    Version of ``LocaleMiddleware`` with modified redirection behavior

    This is needed because the behavior reported at
    https://code.djangoproject.com/ticket/17734 still occurs when using
    Django CMS because the default regex for the page view of Django CMS will
    match most URL paths, causing ``LocaleMiddleware.process_response()``
    to redirect to the CMS view instead of passing through the 404 error
    """

    def _resolves_to_same_view(self, path, language_path, urlconf):
        """Returns true if the raw path and the language-aware path resolve to the same view"""
        path_match = resolve(path, urlconf)
        language_path_match = resolve(language_path, urlconf)
        return path_match == language_path_match

    def process_response(self, request, response):
        language = translation.get_language()
        if (response.status_code == 404 and
                not translation.get_language_from_path(request.path_info)
                    and self.is_language_prefix_patterns_used()):
            urlconf = getattr(request, 'urlconf', None)
            language_path = '/%s%s' % (language, request.path_info)
            valid_language_path = language_path
            path_valid = is_valid_path(language_path, urlconf)
            if (not path_valid and settings.APPEND_SLASH
                    and not language_path.endswith('/')):
                path_valid = is_valid_path("%s/" % language_path, urlconf)
                if path_valid:
                    valid_language_path = "%s/" % language_path

            if path_valid and is_valid_path(request.path_info):
                # If the language path is valid and the request's original path
                # is also valid, make sure we're not redirecting to a different view
                path_valid = self._resolves_to_same_view(request.path_info, valid_language_path, urlconf)

            if path_valid:
                language_url = "%s://%s/%s%s" % (
                    request.is_secure() and 'https' or 'http',
                    request.get_host(), language, request.get_full_path())
                return HttpResponseRedirect(language_url)
        translation.deactivate()

        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = language
        return response
