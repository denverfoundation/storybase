"""Views for storybase_story app"""

from django.template import Context
from django.template.loader import get_template
from django.views.generic import TemplateView 
from django.utils.safestring import mark_safe
from storybase.views.generic import ModelIdDetailView
from storybase_story.api import StoryResource
from storybase_story.models import Story

def simple_story_list(stories):
    """Render a simple listing of stories
    
    Arguments:
    stories -- A queryset of Story model instances

    """
    template = get_template('storybase_story/simple_story_list.html')
    # TODO: Implement this template
    context =  Context({"stories": stories})
    return template.render(context)

def homepage_story_list():
    """Render a listing of stories for the homepage"""
    stories = Story.objects.on_homepage().order_by('-last_edited')
    return simple_story_list(stories)


class ExploreStoriesView(TemplateView):
    template_name = "storybase_story/explore_stories.html"

    def get_context_data(self, **kwargs):
        resource = StoryResource()
	to_be_serialized = resource.explore_get_data_to_be_serialized()
	return {
            'stories_json': mark_safe(resource.serialize(None, to_be_serialized,
                                                         'application/json'))
	}


class StoryDetailView(ModelIdDetailView):
    context_object_name = "story"
    queryset = Story.objects.all()


class StoryViewerView(ModelIdDetailView):
    context_object_name = "story"
    queryset = Story.objects.all()
    template_name = 'storybase_story/story_viewer.html'
