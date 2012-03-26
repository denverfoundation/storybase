from django import forms
from django.db import models

class ShortTextField(models.TextField):
    """ The unlimited length of a TextField, but uses the CharField widget 
    
    There isn't any performance benefit to using varchar in Postgres, so
    it makes sense to use text instead of using varchar with an arbitrary
    charcter limit when the application doesn't call for one.

    Still, in the Django admin or automatically-generated ModelForms, it's
    nice to suggest to the user that this is a line of text rather than
    a block of text, even if the length isn't actually limited.

    See
    http://www.postgresql.org/docs/8.4/interactive/datatype-character.html 

    """
    def formfield(self, **kwargs):
        defaults = {'widget': forms.CharField}
        defaults.update(kwargs)
        return super(ShortTextField, self).formfield(**defaults)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^storybase\.fields\.ShortTextField"])
except ImportError:
    pass
