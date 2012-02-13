from django.contrib import admin
from storybase_asset.models import Asset
from models import Story

class StoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ['title', 'author__first_name', 'author__last_name']
    list_filter = ('status', 'author', 'tags__name')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "assets":
            kwargs["queryset"] = Asset.objects.filter(user=request.user)
        return super(StoryAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
    
admin.site.register(Story, StoryAdmin)
