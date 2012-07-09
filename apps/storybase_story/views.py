"""Views for storybase_story app"""

import json

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template import Context
from django.template.loader import get_template
from django.views.generic import TemplateView 
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe

from storybase.utils import simple_language_changer
from storybase.views.generic import ModelIdDetailView
from storybase_story.api import StoryResource, StoryTemplateResource
from storybase_story.models import Story

def simple_story_list(stories):
    """Render a simple listing of stories
    
    Arguments:
    stories -- A queryset of Story model instances

    """
    template = get_template('storybase_story/simple_story_list.html')
    context =  Context({"stories": stories})
    return template.render(context)

def homepage_story_list(num_stories):
    """Render a listing of stories for the homepage"""
    stories = Story.objects.on_homepage().order_by('-last_edited')[:num_stories]
    return simple_story_list(stories)


class ExploreStoriesView(TemplateView):
    """
    A view that lets users filter a list of stories

    The heavy lifting is done by ```StoryResource``` and client-side 
    JavaScript.

    """
    template_name = "storybase_story/explore_stories.html"

    @method_decorator(simple_language_changer)
    def dispatch(self, *args, **kwargs):
        return super(ExploreStoriesView, self).dispatch(*args, **kwargs)

    def _get_selected_filters(self):
        """
        Build a data structure of selected filters

        The selected filters are based on the parameters passed in request.GET

        The returned data structure is meant to be serialized and passed to
        client-side code.

        """
        selected_filters = {}
        for filter in StoryResource._meta.explore_filter_fields:
            values = self.request.GET.get(filter, None)
            if values:
                selected_filters[filter] = values.split(",")
        return selected_filters

    def _get_selected_view_type(self):
        """
        Set the default view (tile, list, map) based on a request parameter
        or set a reasonable default.
        """
        view_type = self.request.GET.get('view', 'tile')
        view_type = view_type if view_type in ('tile', 'list', 'map') else 'tile'
        return view_type

    def get_context_data(self, **kwargs):
        resource = StoryResource()
        to_be_serialized = resource.explore_get_data_to_be_serialized(self.request)
        return {
            'stories_json': mark_safe(resource.serialize(None, to_be_serialized,
                                                         'application/json')),
            'selected_filters': mark_safe(json.dumps(self._get_selected_filters())),
            'view_type': mark_safe(json.dumps(self._get_selected_view_type()))
        }


class StoryDetailView(ModelIdDetailView):
    context_object_name = "story"
    queryset = Story.objects.all()


class StoryViewerView(ModelIdDetailView):
    context_object_name = "story"
    queryset = Story.objects.all()
    template_name = 'storybase_story/story_viewer.html'


class StoryBuilderView(TemplateView):
    """
    Story builder view

    The heavy lifting is done by the REST API and client-side JavaScript

    """
    template_name = "storybase_story/story_builder.html"

    def get_context_data(self, **kwargs):
        """Provide Bootstrap data for Backbone models and collections"""
        to_be_serialized = {}

        # Use the Tastypie resource to retrieve a JSON list of story
        # templates.  
        # See http://django-tastypie.readthedocs.org/en/latest/cookbook.html#using-your-resource-in-regular-views
        # and ModelResource.get_list()
        resource = StoryTemplateResource()
        objects = resource.obj_get_list()
        bundles = [resource.build_bundle(obj=obj) for obj in objects]
        to_be_serialized['objects'] = [resource.full_dehydrate(bundle) for bundle in bundles]

        return {
            'story_template_json': mark_safe(resource.serialize(None, to_be_serialized, 'application/json')),
        }

        @method_decorator(login_required)
        def dispatch(self, *args, **kwargs):
            # We override the view's dispatch method so we can decorate
            # it to only allow access by logged-in users
            return super(StoryBuilderView, self).dispatch(*args, **kwargs)
