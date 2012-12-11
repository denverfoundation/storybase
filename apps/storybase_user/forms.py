from django.conf import settings
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from filer.models import Image

from storybase.utils import is_file
from storybase.forms import (FileOrUrlField, TranslatedModelForm,
        UserEmailField)
from storybase_asset.models import (create_local_image_asset,
        create_external_asset)
from storybase_user.models import Organization, UserProfile

class OrganizationModelForm(TranslatedModelForm):
    members = UserEmailField(required=False, 
            help_text=_("Enter a comma-separated list of email addresses "
                        "of the users you would like to add to your "
                        "organization.  The email addresses must match "
                        "those of valid %s users." % (
                            settings.STORYBASE_SITE_NAME)))
    image = FileOrUrlField(required=False)

    class Meta:
        model = Organization
        fields = ('website_url', 'members',)
        translated_fields = ('name', 'description',)

    def save(self, commit=True):
        instance = super(OrganizationModelForm, self).save(commit)
        image_asset = None
        img_val = self.cleaned_data.get('image', None)
        if img_val: 
            if is_file(img_val):
                image_asset = create_local_image_asset('image', img_val, img_val.name)

            instance.featured_assets.add(image_asset)
        return instance


class UserNotificationsForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('notify_updates', 'notify_admin', 'notify_digest',
                  'notify_story_featured', 'notify_story_comment')
