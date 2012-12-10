from django.conf import settings
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from storybase.forms import TranslatedModelForm, UserEmailField
from storybase_user.models import Organization, UserProfile

class OrganizationModelForm(TranslatedModelForm):
    members = UserEmailField(required=False, 
            help_text=_("Enter a comma-separated list of email addresses "
                        "of the users you would like to add to your "
                        "organization.  The email addresses must match "
                        "those of valid %s users." % (
                            settings.STORYBASE_SITE_NAME)))

    class Meta:
        model = Organization
        fields = ('website_url', 'members',)
        translated_fields = ('name', 'description',)


class UserNotificationsForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('notify_updates', 'notify_admin', 'notify_digest',
                  'notify_story_featured', 'notify_story_comment')
