import django

from django.template import Library

# Always create a variable named register, even if we don't need to
# load this backport, otherwise {% load storybase_i18n %} will fail
register = Library()

if django.VERSION[0] <=1 and django.VERSION[2] < 4: 
    # Make the ``langauge`` template tag available for Django versions earlier
    # than 1.4

    # Copyright (c) Django Software Foundation and individual contributors.
    # All rights reserved.
    #
    # Redistribution and use in source and binary forms, with or without
    # modification, are permitted provided that the following conditions 
    # are met:
    # 
    #
    #    1. Redistributions of source code must retain the above copyright 
    #       notice, this list of conditions and the following disclaimer.
    #      
    #    
    #    2. Redistributions in binary form must reproduce the above copyright 
    #       notice, this list of conditions and the following disclaimer in the
    #       documentation and/or other materials provided with the 
    #       distribution.
    #
    #    3. Neither the name of Django nor the names of its contributors may 
    #       be used to endorse or promote products derived from this software 
    #       without specific prior written permission.
    #      
    #
    # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS 
    # IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED 
    # TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A 
    # PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER 
    # OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
    # EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
    # PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR 
    # PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
    # LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT  (INCLUDING   
    # NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    # SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
   
    from django.template import (Node, TemplateSyntaxError)
    from django.utils.translation import (activate, deactivate, deactivate_all,
        get_language)


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
            raise TemplateSyntaxError("'%s' takes one argument (language)" %
                                      bits[0])
        language = parser.compile_filter(bits[1])
        nodelist = parser.parse(('endlanguage',))
        parser.delete_first_token()
        return LanguageNode(nodelist, language)
