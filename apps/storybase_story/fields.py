"""Custom fields"""

from django import forms

class SectionModelChoiceField(forms.ModelChoiceField):
    """
    Custom ModelChoiceField that shows both a Section's title and 
    its Story's title

    This helps admins differentiate between Sections with the same name in
    different Stories.

    """
    def label_from_instance(self, obj):
        return "%s (%s)" % (obj.title, obj.story.title)
