"""Views for storybase_story app"""

import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.template import Context
from django.template.loader import get_template
from django.views.generic import View, DetailView, TemplateView 
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from storybase_asset.api import AssetResource
from storybase_asset.models import ASSET_TYPES
from storybase_geo.models import Place
from storybase_help.api import HelpResource
from storybase_story.api import (ContainerTemplateResource,
    SectionAssetResource, SectionResource,
    StoryResource, StoryTemplateResource)
from storybase_story.models import SectionLayout, Story, StoryTemplate
from storybase_taxonomy.models import Category
from storybase.utils import simple_language_changer
from storybase.views.generic import ModelIdDetailView

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

def homepage_banner_list(num_stories):
    """Render a listing of stories for the homepage banner """
    # temp -- just putting out demo images
    #stories = Story.objects.on_homepage().order_by('-last_edited')[:num_stories]
    stories = []
    image_num = 1
    for i in range(num_stories):
        image_num = i + 1
        if (image_num > 9):
            image_num -= 9
        stories.append({"image": "image%d.jpg" % image_num, "title": "banner story %d title here." % i})
    return stories



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
    queryset = Story.objects.exclude(source__relation_type='connected')


class StoryViewerView(ModelIdDetailView):
    context_object_name = "story"
    queryset = Story.objects.exclude(source__relation_type='connected')
    template_name = 'storybase_story/story_viewer.html'

    def get_context_data(self, **kwargs):
        context = super(StoryViewerView, self).get_context_data(**kwargs)
        preview = self.kwargs.get('preview', False)
        if preview and self.request.user:
            # Previewing the story in the viewer, include draft
            # connected stories belonging to this user
            context['connected_stories'] = self.object.connected_stories(published_only=False, draft_author=self.request.user)

        if 'connected_stories' not in context:
            # Viewing the story in the viewer, show only published
            # connected stories
            context['connected_stories'] = self.object.connected_stories()

        context['sections_json'] = self.object.structure.sections_json(
                connected_stories=context['connected_stories'])

        return context


class StoryUpdateView(SingleObjectMixin, SingleObjectTemplateResponseMixin, View):
  """
  Updates story status, redirects to My Stories.
  TODO: post success notification.
  """
  queryset = Story.objects.all()
  template_name = 'storybase_story/story_update.html'
  slug_url_kwarg = 'slug'
  
  def update_story(self, obj_id, status):
    obj = self.get_object()
    if obj is not None:
      if not obj.has_perm(self.request.user, 'change'):
          raise PermissionDenied(_(u"You are not authorized to edit this story"))
      obj.status = status
      obj.save()
  
  def get(self, request, *args, **kwargs):
    self.object = self.get_object()

    # previous and next urls default to account story list
    result_url = previous_url = reverse('account_stories')
    
    if 'HTTP_REFERER' in request.META:
      previous_url = request.META['HTTP_REFERER']

    # can specify result url destination in GET query and urlconf.
    if 'result_url' in kwargs and kwargs['result_url'] is not None:
      result_url = kwargs['result_url']
    if 'result_url' in request.GET:
      result_url = request.GET['result_url']
    
    context = self.get_context_data(object=self.object, result_url=result_url, previous_url=previous_url, **kwargs)
    return self.render_to_response(context)
  
  def post(self, request, *args, **kwargs):
    if self.request.user.is_authenticated():
      self.update_story(request.POST['story_id'], kwargs['status'])
    result_url = reverse('account_stories')
    if 'result_url' in kwargs and kwargs['result_url'] is not None:
      result_url = kwargs['result_url']
    if 'result_url' in request.POST:
      result_url = request.POST['result_url']
    # TODO: success notification?
    return HttpResponseRedirect(result_url)
    

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

    def get_source_story(self):
        """Get the source story for a connected story"""
        queryset = self.get_queryset()
        source_story_id = self.kwargs.get('source_story_id', None)
        source_slug = self.kwargs.get('source_slug', None)
        if source_story_id is not None:
            queryset = queryset.filter(story_id=source_story_id)
        elif source_slug is not None:
            queryset = queryset.filter(slug=source_slug)
        else:
            return None

        try:
            source_story = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                    {'verbose_name': queryset.model._meta.verbose_name})
        if not source_story.allow_connected:
            raise PermissionDenied(_(u"This story does not allow connected stories"))

        return source_story

    def get_template_object(self, queryset=None):
        """
        Get the ``StoryTemplate`` instance for this view

        The template model instance is used to initialize the structure of the newly
        created Story model instance.

        The template is identified with a 'template' parameter in the
        querystring of the view URL or view keyword arguments.
        It can either be a value for the template_id or slug field of 
        the the ``StoryTemplate`` model.

        This method returns None if no matching story is found or if no
        template identifier is provided.  This will cause the builder
        to be launched with the select template step.

        """
        obj = None
        template_slug_or_id = self.kwargs.get('template', None)
        if template_slug_or_id is None:
            # Template identifier not in keyword arguments. Try
            # getting it from URL query string
            template_slug_or_id = self.request.GET.get('template', None)
        if template_slug_or_id:
            if queryset is None:
                queryset = StoryTemplate.objects.all()

            q = Q(template_id=template_slug_or_id)
            q = q | Q(slug=template_slug_or_id)
            queryset = queryset.filter(q)

            try:
                obj = queryset.get()
            except ObjectDoesNotExist:
                # If a matching template doesn't exist, just return
                # None. The user will be prompted to select a template
                # in the builder
                pass

        return obj 

    def get_story_json(self, obj=None):
        if obj is None:
            obj = self.object
        resource = StoryResource()
        bundle = resource.build_bundle(obj=obj)
        to_be_serialized = resource.full_dehydrate(bundle)
        return resource.serialize(None, to_be_serialized, 'application/json')

    def get_sections_json(self, story=None):
        """
        Get serialized section data for a story

        This is used to add JSON data to the view's response context in
        order to bootstrap Backbone models and collections.
        
        """
        if story is None:
            story = self.object
        resource = SectionResource()
        to_be_serialized = {}
        objects = resource.obj_get_list(story__story_id=story.story_id)
        sorted_objects = resource.apply_sorting(objects)
        to_be_serialized['objects'] = sorted_objects

        # Dehydrate the bundles in preparation for serialization.
        bundles = [resource.build_bundle(obj=obj) for obj in to_be_serialized['objects']]
        to_be_serialized['objects'] = [resource.full_dehydrate(bundle) for bundle in bundles]
        to_be_serialized = resource.alter_list_data_to_serialize(request=None, data=to_be_serialized)
        return resource.serialize(None, to_be_serialized, 'application/json')

    def get_section_assets_json(self, story=None):
        """
        Get serialized asset data for a story by section

        This is used to add JSON data to the view's response context in
        order to bootstrap Backbone models and collections.
        
        The response JSON is an object keyed with the section IDs.
        The asset data is accessible via the objects property of
        each section object.
        
        """
        if story is None:
            story = self.object
        resource = SectionAssetResource()
        to_be_serialized = {}
        for section in story.sections.all():
            sa_to_be_serialized = {}
            objects = resource.obj_get_list(section__section_id=section.section_id)
            sorted_objects = resource.apply_sorting(objects)
            sa_to_be_serialized['objects'] = sorted_objects

            # Dehydrate the bundles in preparation for serialization.
            bundles = [resource.build_bundle(obj=obj) for obj in sa_to_be_serialized['objects']]
            sa_to_be_serialized['objects'] = [resource.full_dehydrate(bundle) for bundle in bundles]
            sa_to_be_serialized = resource.alter_list_data_to_serialize(request=None, data=sa_to_be_serialized)
            to_be_serialized[section.section_id] = sa_to_be_serialized

        return resource.serialize(None, to_be_serialized, 'application/json')

    def get_assets_json(self, story=None, featured=False):
        if story is None:
            story = self.object
        resource = AssetResource()
        to_be_serialized = {}
        objects = resource.obj_get_list(self.request, featured=featured,
                                        story_id=story.story_id)
        sorted_objects = resource.apply_sorting(objects)
        to_be_serialized['objects'] = sorted_objects

        # Dehydrate the bundles in preparation for serialization.
        bundles = [resource.build_bundle(obj=obj) for obj in to_be_serialized['objects']]
        to_be_serialized['objects'] = [resource.full_dehydrate(bundle) for bundle in bundles]
        to_be_serialized = resource.alter_list_data_to_serialize(request=None, data=to_be_serialized)
        return resource.serialize(None, to_be_serialized, 'application/json')

    def get_story_template_json(self):
        to_be_serialized = {}
        resource = StoryTemplateResource()
        objects = resource.obj_get_list()
        bundles = [resource.build_bundle(obj=obj) for obj in objects]
        to_be_serialized['objects'] = [resource.full_dehydrate(bundle) for bundle in bundles]
        return resource.serialize(None, to_be_serialized, 'application/json')

    def get_layouts_json(self):
        to_be_serialized = [{'name': layout.name,
                             'layout_id': layout.layout_id,
                             'slug': layout.slug} for layout
                            in SectionLayout.objects.all()]
        return json.dumps(to_be_serialized)

    def get_asset_types_json(self):
        to_be_serialized = [{'name': asset_type[1], 'type': asset_type[0]} for asset_type in ASSET_TYPES]
        return json.dumps(to_be_serialized)

    def get_help_json(self):
        # Lookup keys to filter help items to include
        help_slugs = ['story-information', 'call-to-action', 'new-section']
        to_be_serialized = {}
        resource = HelpResource()
        objects = resource.obj_get_list().filter(slug__in=help_slugs)
        bundles = [resource.build_bundle(obj=obj) for obj in objects]
        to_be_serialized['objects'] = [resource.full_dehydrate(bundle) for bundle in bundles]
        return resource.serialize(None, to_be_serialized, 'application/json')

    def get_topics_json(self):
        to_be_serialized =[{ 'id': obj.pk, 'name': obj.name } 
                           for obj in Category.objects.order_by('categorytranslation__name')]
        return json.dumps(to_be_serialized)

    def get_places_json(self):
        to_be_serialized = [{ 'id': place.place_id, 'name': place.name }
                            for place in Place.objects.order_by('geolevel__name', 'name')]
        return json.dumps(to_be_serialized)

    def get_organizations_json(self):
        to_be_serialized = [{'organization_id': org.organization_id,
                             'name': org.name}
                            for org in self.request.user.organizations.all()]
        return json.dumps(to_be_serialized);

    def get_projects_json(self):
        # TODO: Update this to include "Open Projects"
        to_be_serialized = [{'project_id': project.project_id,
                             'name': project.name}
                            for project in self.request.user.projects.all()]
        return json.dumps(to_be_serialized);

    def get_related_stories_json(self):
        if self.source_story:
            return json.dumps({
                'objects': [
                    {
                        'source': self.source_story.story_id,
                        'relation_type': 'connected'
                    },
                ]
            })
        else:
            return None

    def get_prompt(self):
        """
        Get the story prompt
        """
        if self.object:
            return self.object.get_prompt()
        elif self.source_story and self.source_story.connected_prompt:
            return self.source_story.connected_prompt;
        else:
            return "";

    def get_container_templates_json(self, story=None):
        if story is None:
            story = self.object
        resource = ContainerTemplateResource()
        to_be_serialized = {}
        objects = resource.obj_get_list(self.request,
                                        story_id=story.story_id)
        sorted_objects = resource.apply_sorting(objects)
        to_be_serialized['objects'] = sorted_objects

        # Dehydrate the bundles in preparation for serialization.
        bundles = [resource.build_bundle(obj=obj) for obj in to_be_serialized['objects']]
        to_be_serialized['objects'] = [resource.full_dehydrate(bundle) for bundle in bundles]
        to_be_serialized = resource.alter_list_data_to_serialize(request=None, data=to_be_serialized)
        return resource.serialize(None, to_be_serialized, 'application/json')


    def get_options_json(self):
        """Get configuration options for the story builder"""
        options = {
            'defaultImageUrl': Story.get_default_img_url(335, 200),
            # Show only the builder workflow steps
            'visibleSteps': {
                'build': True,
                'data': True, 
                'tag': True,
                'review': True,
                'publish': True
            },
            # Show the view that allows the user to edit
            # the story title and byline
            'showStoryInformation': True,
            # Show the view that allows the user to edit the call
            # to action or enable connected stories
            'showCallToAction': True,
            # Show a list of sections that the user can use to navigate
            # between sectons
            'showSectionList': True,
            # Show the input for editing section titles
            'showSectionTitles': True,
            # Show the select input for changing section layouts
            'showLayoutSelection': True,
            # Show the story title input in the section edit view 
            'showStoryInfoInline': False,
            # Prompt (for connected stories)
            'prompt': self.get_prompt(),
            # Show the sharing view
            'showSharing': True,
            # Show the builder tour
            'showTour': True,
            # Force showing the tour, even if the cookie has been set
            'forceTour': getattr(settings, 'STORYBASE_FORCE_BUILDER_TOUR',
                                 False),
            # Endpoint for fetching license information
            'licenseEndpoint': reverse("api_cc_license_get"),
            # Site name (used for re-writing title)
            'siteName': settings.STORYBASE_SITE_NAME,
            # Template for generating preview URLs
            'previewURLTemplate': '/stories/{{id}}/preview/',
        }
        if (self.template_object and self.template_object.slug == settings.STORYBASE_CONNECTED_STORY_TEMPLATE):
            # TODO: If these settings apply in cases other than just
            # connected stories, it might make more sense to store them
            # as part of the template model
            options.update({
                'visibleSteps': {
                    'build': True,
                    'publish': True
                },
                'showStoryInformation': False,
                'showCallToAction': False,
                'showSectionList': False,
                'showSectionTitles': False,
                'showLayoutSelection': False,
                'showStoryInfoInline': True,
                'showSharing': False,
                'showTour': False,
                'previewURLTemplate': '/stories/%s/preview/#connected-stories/{{id}}' % (self.source_story.story_id)
            })
        return json.dumps(options)

    def get_context_data(self, **kwargs):
        """Bootstrap data for Backbone models and collections"""
        context = {
            'asset_types_json': mark_safe(self.get_asset_types_json()),
            'help_json': mark_safe(self.get_help_json()),
            'layouts_json': mark_safe(self.get_layouts_json()),
            'organizations_json': mark_safe(self.get_organizations_json()),
            'places_json': mark_safe(self.get_places_json()),
            'projects_json': mark_safe(self.get_projects_json()),
            'story_template_json': mark_safe(self.get_story_template_json()),
            'topics_json': mark_safe(self.get_topics_json()),
        }

        if self.object:
            context['story_json'] = mark_safe(self.get_story_json())
            context['featured_assets_json'] = mark_safe(self.get_assets_json(featured=True))
            context['assets_json'] = mark_safe(self.get_assets_json())
            if self.object.template_story:
                context['template_story_json'] = mark_safe(
                    self.get_story_json(self.object.template_story))
                context['template_sections_json'] = mark_safe(
                    self.get_sections_json(self.object.template_story))
                context['container_templates_json'] = mark_safe(self.get_container_templates_json(self.object.template_story))
        elif self.template_object:
            context['template_story_json'] = mark_safe(
                self.get_story_json(self.template_object.story))
            context['template_sections_json'] = mark_safe(
                self.get_sections_json(self.template_object.story))
            context['container_templates_json'] = mark_safe(
                self.get_container_templates_json(self.template_object.story))

        related_stories_json = self.get_related_stories_json()
        if related_stories_json: 
            context['related_stories_json'] = mark_safe(
                related_stories_json)

        context['options_json'] = mark_safe(self.get_options_json())

        return context

    def get(self, request, **kwargs):
        self.object = self.get_object()
        self.template_object = self.get_template_object(queryset=None)
        self.source_story = self.get_source_story()
        context = self.get_context_data(object=self.object, **kwargs)
        return self.render_to_response(context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # We override the view's dispatch method so we can decorate
        # it to only allow access by logged-in users
        return super(StoryBuilderView, self).dispatch(*args, **kwargs)


class StoryWidgetView(ModelIdDetailView):
    """An embedable widget for a story"""
    context_object_name = "story"
    # You can only embed published stories
    queryset = Story.objects.filter(status='published')
    template_name = 'storybase_story/story_widget.html'


class StoryShareWidgetView(ModelIdDetailView):
    """
    Widget for sharing a story

    While ``StoryWidgetView`` provides the HTML for the widget embedded
    in a partner website, this view provides the HTML for a popup window
    of sharing tools.  It is designed to be fetched via an asynchronous 
    request from JavaScript

    """
    context_object_name = "story"
    queryset = Story.objects.filter(status='published')
    template_name = 'storybase_story/story_share_widget.html'
