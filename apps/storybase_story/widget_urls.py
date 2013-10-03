from django.conf.urls import patterns, url

from storybase_story.views import StoryWidgetView

urlpatterns = patterns('',
    url(r'^widget/$', StoryWidgetView.as_view(), name='story_widget'),
    url(r'^widget/0.1/$',
        StoryWidgetView.as_view(), {'version': '0.1'}, name='story_widget'),
)
