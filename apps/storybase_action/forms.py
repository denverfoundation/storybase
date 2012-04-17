"""Custom forms for action app"""

from django.forms import ModelForm

from storybase_action.models import SiteContactMessage

class SiteContactMessageForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = SiteContactMessage
