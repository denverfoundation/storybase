
from tastypie import fields
from tastypie.authentication import Authentication

from storybase.api import (DelayedAuthorizationResource,
    TranslatedModelResource, LoggedInAuthorization)
from storybase_asset.models import Asset

class AssetResource(DelayedAuthorizationResource, TranslatedModelResource):
    # Explicitly declare fields that are on the translation model, or the
    # subclass
    title = fields.CharField(attribute='title', null=True)
    body = fields.CharField(attribute='body', null=True)
    url = fields.CharField(attribute='url', null=True)

    class Meta:
        queryset = Asset.objects.select_subclasses()
        resource_name = 'assets'
        allowed_methods = ['get', 'post', 'patch']
        authentication = Authentication()
        authorization = LoggedInAuthorization()

        delayed_authorization_methods = []

    def get_object_list(self, request):
        """
        Get a list of assets, filtering based on the request's user and 
        the publication status
        
        """
        from django.db.models import Q
        # Only show published stories  
        q = Q(status='published')
        if hasattr(request, 'user') and request.user.is_authenticated():
            # If the user is logged in, show their unpublished stories as
            # well
            q = q | Q(author=request.user)

        return super(AssetResource, self).get_object_list(request).filter(q)
