from django.forms import ModelChoiceField, ModelForm
from django.forms.widgets import HiddenInput, MultipleHiddenInput

from storybase_messaging.models import SiteContactMessage, StoryContactMessage

from storybase_story.models import Story


class SiteContactMessageForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = SiteContactMessage
        fields = ['name', 'email', 'phone', 'message']


class StoryContactMessageForm(ModelForm):
    story = ModelChoiceField(queryset=Story.objects.all(),
                             widget=HiddenInput())
    required_css_class = 'required'

    class Meta:
        model = StoryContactMessage
        fields = ['name', 'email', 'message', 'story']
