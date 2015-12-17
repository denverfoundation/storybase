from django.conf import settings
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from storybase.utils import is_file
from storybase.forms import (FileOrUrlField, TranslatedModelForm,
        UserEmailField)
from storybase_asset.models import (create_local_image_asset,
        create_external_asset)
from storybase_user.models import (Organization, Project, UserProfile)


class StoryAggregatorModelFormBase(TranslatedModelForm):
    required_css_class = 'required'

    members = UserEmailField(required=False,
            help_text=_("Enter a comma-separated list of email addresses "
                        "of the users you would like to add. "
                        "The email addresses must match "
                        "those of valid %s users." % (
                            settings.STORYBASE_SITE_NAME)))
    image = FileOrUrlField(required=False)

    def save(self, commit=True):
        instance = super(StoryAggregatorModelFormBase, self).save(commit)
        through_field_name = self._meta.model._meta.object_name.lower()
        for user in self.cleaned_data.get('members'):
            through_kwargs = {
                'user': user,
                through_field_name: instance,
                'member_type': 'member',
            }
            self._meta.model.members.through.objects.create(
                    **through_kwargs)
        image_asset = None
        img_val = self.cleaned_data.get('image', None)
        if img_val:
            if is_file(img_val):
                image_asset = create_local_image_asset('image', img_val, img_val.name)
            else:
                image_asset = create_external_asset('image',
                        url=img_val)

            instance.featured_assets.add(image_asset)
        return instance


class OrganizationModelForm(StoryAggregatorModelFormBase):
    class Meta:
        model = Organization
        fields = ('contact_info', 'website_url',)
        translated_fields = ('name', 'description',)


class ProjectModelForm(StoryAggregatorModelFormBase):
    class Meta:
        model = Project
        fields = ('website_url',)
        translated_fields = ('name', 'description',)


class UserNotificationsForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('notify_admin', 'notify_digest',
                  'notify_story_unpublished', 'notify_story_published',
                  'notify_story_comment')
