from django.contrib import admin
from models import ExternalAsset, HtmlAsset

class AssetAdmin(admin.ModelAdmin):
    list_display = ('title',)

admin.site.register(ExternalAsset, AssetAdmin)
admin.site.register(HtmlAsset, AssetAdmin)
