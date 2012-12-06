from django.forms import ModelForm

from storybase.forms import TranslatedModelForm
from storybase_user.models import Organization, UserProfile

class OrganizationModelForm(TranslatedModelForm):
    class Meta:
        model = Organization
        fields = ('website_url',)
        translated_fields = ('name', 'description',)


class UserNotificationsForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('notify_updates', 'notify_admin', 'notify_digest',
                  'notify_story_featured', 'notify_story_comment')
