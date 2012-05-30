import django

if django.VERSION[0] <=1 and django.VERSION[2] < 4: 
    # Make the ``langauge`` template tag available for Django versions earlier
    # than 1.4
    from django.template import (Node, Library, TemplateSyntaxError)
    from django.utils.translation import (activate, deactivate, deactivate_all,
        get_language)

    register = Library()

    class Override(object):
        def __init__(self, language, deactivate=False):
            self.language = language
            self.deactivate = deactivate
            self.old_language = get_language()

        def __enter__(self):
            if self.language is not None:
                activate(self.language)
            else:
                deactivate_all()

        def __exit__(self, exc_type, exc_value, traceback):
            if self.deactivate:
                deactivate()
            else:
                activate(self.old_language)

    class LanguageNode(Node):
        def __init__(self, nodelist, language):
            self.nodelist = nodelist
            self.language = language

        def render(self, context):
            with Override(self.language.resolve(context)):
                output = self.nodelist.render(context)
                return output

    @register.tag
    def language(parser, token):
        """
        This will enable the given language just for this block.

        Usage::

            {% language "de" %}
                This is {{ bar }} and {{ boo }}.
            {% endlanguage %}

        """
        bits = token.split_contents()
        if len(bits) != 2:
            raise TemplateSyntaxError("'%s' takes one argument (language)" % bits[0])
        language = parser.compile_filter(bits[1])
        nodelist = parser.parse(('endlanguage',))
        parser.delete_first_token()
        return LanguageNode(nodelist, language)
