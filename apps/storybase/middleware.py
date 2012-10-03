import lxml.html

from django.shortcuts import render_to_response

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
