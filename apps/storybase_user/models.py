from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

class Provider(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        abstract = True

class Credential(models.Model):
    CREDENTIAL_TYPES = (
      (u'oauth', u'oAuth'),
    )
    user = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_credentials")
    type = models.CharField(max_length=10, choices=CREDENTIAL_TYPES)
    
    class Meta:
        abstract = True

class OAuthProvider(Provider):
    request_token_url = models.URLField() 
    access_token_url = models.URLField() 
    authorize_url = models.URLField()
    client_token = models.CharField(max_length=200)
    client_secret = models.CharField(max_length=200)

class OAuthProviderAdmin(admin.ModelAdmin):
    list_display = ('name',)

class OAuth2Provider(Provider):
    base_url = models.URLField() 
    client_id = models.CharField(max_length=200)
    client_secret = models.CharField(max_length=200)

class OAuth2ProviderAdmin(admin.ModelAdmin):
    list_display = ('name',)

class OAuthCredential(Credential):
    token = models.CharField(max_length=200)
    secret = models.CharField(max_length=200)
    provider = models.ForeignKey(OAuthProvider, related_name="credentials")
    
    def __init__(self, *args, **kwargs):
        super(OAuthCredential, self).init(*args, **kwargs)
        self.type = 'oauth'


admin.site.register(OAuth2Provider, OAuth2ProviderAdmin)
admin.site.register(OAuthCredential)

