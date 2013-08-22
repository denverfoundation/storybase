"""
Handlebars templates use constructs like:

    {{if condition}} print something{{/if}}

This, of course, completely screws up Django templates,
because Django thinks {{ and }} mean something.

Wrap {% verbatim %} and {% endverbatim %} around those
blocks of Handlebars templates and this will try its best
to output the contents with no changes.
"""

from django import template

register = template.Library()

# For Django >= 1.5, use the default verbatim tag implementation
if not hasattr(template.defaulttags, 'verbatim'):
    class VerbatimNode(template.Node):

        def __init__(self, text):
            self.text = text
        
        def render(self, context):
            return self.text


    @register.tag
    def verbatim(parser, token):
        text = []
        while 1:
            token = parser.tokens.pop(0)
            if token.contents == 'endverbatim':
                break
            if token.token_type == template.TOKEN_VAR:
                text.append('{{')
            elif token.token_type == template.TOKEN_BLOCK:
                text.append('{%')
            text.append(token.contents)
            if token.token_type == template.TOKEN_VAR:
                text.append('}}')
            elif token.token_type == template.TOKEN_BLOCK:
                text.append('%}')
        return VerbatimNode(''.join(text))
