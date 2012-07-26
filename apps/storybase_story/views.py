"""Views for storybase_story app"""

import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404
from django.utils.decorators import method_decorator
from django.template import Context
from django.template.loader import get_template
from django.views.generic import DetailView, TemplateView 
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from storybase.utils import simple_language_changer
from storybase.views.generic import ModelIdDetailView
from storybase_asset.models import ASSET_TYPES
from storybase_help.api import HelpResource
from storybase_story.api import StoryResource, StoryTemplateResource
from storybase_story.models import SectionLayout, Story

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


class StoryBuilderView(DetailView):
    """
    Story builder view

    The heavy lifting is done by the REST API and client-side JavaScript

    """
    queryset = Story.objects.all()
    template_name = "storybase_story/story_builder.html"

    def get_object(self):
        """Retrieve the object by it's model specific id instead of pk"""
        queryset = self.get_queryset()
        obj_id_name = 'story_id'
        obj_id = self.kwargs.get(obj_id_name, None)
        if obj_id is not None:
            filter_args = {obj_id_name: obj_id}
            queryset = queryset.filter(**filter_args)
            try:
                obj = queryset.get()
            except ObjectDoesNotExist:
                raise Http404(_(u"No %(verbose_name)s found matching the query") %
                        {'verbose_name': queryset.model._meta.verbose_name})
            if not obj.has_perm(self.request.user, 'change'):
                raise PermissionDenied(_(u"You are not authorized to edit this story"))
            return obj
        else:
            return None

    def get_story_json(self):
        resource = StoryResource()
        bundle = resource.build_bundle(obj=self.object)
        to_be_serialized = resource.full_dehydrate(bundle)
        return resource.serialize(None, to_be_serialized, 'application/json')

    def get_story_template_json(self):
        to_be_serialized = {}
        resource = StoryTemplateResource()
        objects = resource.obj_get_list()
        bundles = [resource.build_bundle(obj=obj) for obj in objects]
        to_be_serialized['objects'] = [resource.full_dehydrate(bundle) for bundle in bundles]
        return resource.serialize(None, to_be_serialized, 'application/json')

    def get_layouts_json(self):
        to_be_serialized = [{'name': layout.name, 'layout_id': layout.layout_id} for layout in SectionLayout.objects.all()]
        return json.dumps(to_be_serialized)

    def get_asset_types_json(self):
        to_be_serialized = [{'name': asset_type[1], 'type': asset_type[0]} for asset_type in ASSET_TYPES]
        return json.dumps(to_be_serialized)

    def get_help_json(self):
        # Lookup keys to filter help items to include
        help_slugs = ['story-information', 'call-to-action']
        to_be_serialized = {}
        resource = HelpResource()
        objects = resource.obj_get_list().filter(slug__in=help_slugs)
        bundles = [resource.build_bundle(obj=obj) for obj in objects]
        to_be_serialized['objects'] = [resource.full_dehydrate(bundle) for bundle in bundles]
        return resource.serialize(None, to_be_serialized, 'application/json')

    def get_context_data(self, **kwargs):
        """Provide Bootstrap data for Backbone models and collections"""
        context = {
            'layouts_json': mark_safe(self.get_layouts_json()),
            'story_template_json': mark_safe(self.get_story_template_json()),
            'asset_types_json': mark_safe(self.get_asset_types_json()),
            'help_json': mark_safe(self.get_help_json()),
        }

        if self.object:
            context['story_json'] = mark_safe(self.get_story_json())

        return context

    def get(self, request, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object, **kwargs)
        return self.render_to_response(context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # We override the view's dispatch method so we can decorate
        # it to only allow access by logged-in users
        print kwargs
        return super(StoryBuilderView, self).dispatch(*args, **kwargs)
