from django.conf import settings
from django.template import Library, Node
from django.template.loader import render_to_string

from storybase.templatetags import (parse_args_kwargs_and_as_var,
    resolve_args_and_kwargs)

register = Library()

class AddThisWidgetNode(Node):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def _get_template_context(self, url=None, size=None, include_js=True):
        context = {
            'url': url,
            'include_js': include_js,
            'addthis_pubid': getattr(settings, 'ADDTHIS_PUBID', None),
        }

        if size is not None:
            context['addthis_size_style'] = 'addthis_%s_style' % (size)

        return context

    def render(self, context):
        args, kwargs = resolve_args_and_kwargs(self.args, self.kwargs, context)
        template_context = self._get_template_context(*args, **kwargs)
        return render_to_string('addthis_widget.html', template_context)

@register.tag
def addthis_widget(parser, token):
    bits = token.split_contents()
    args = []
    kwargs = {}

    if len(bits) > 1:
        args, kwargs, asvar = parse_args_kwargs_and_as_var(parser, bits[1:])

    return AddThisWidgetNode(*args, **kwargs)
