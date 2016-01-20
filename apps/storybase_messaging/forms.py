from django.forms import ModelForm

from storybase_messaging.models import SiteContactMessage


class SiteContactMessageForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = SiteContactMessage
        fields = ['name', 'email', 'phone', 'message']


class StoryContactMessageForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = SiteContactMessage
        fields = ['name', 'email', 'message']
