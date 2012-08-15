from django.forms import ModelForm

from storybase_user.models import UserProfile

class UserNotificationsForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('notify_updates', 'notify_admin', 'notify_digest', 'notify_story_featured', 'notify_story_comment')
