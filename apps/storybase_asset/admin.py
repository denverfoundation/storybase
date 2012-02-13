from django.contrib import admin
from models import ExternalAsset

class AssetAdmin(admin.ModelAdmin):
    list_display = ('title',)

admin.site.register(ExternalAsset, AssetAdmin)
