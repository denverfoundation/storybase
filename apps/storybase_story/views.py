"""Views for storybase_story app"""

import json
import re
import urlparse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import resolve, reverse, get_script_prefix, Resolver404
from django.db.models import Q
from django.forms.widgets import HiddenInput
from django.http import Http404, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.views.generic import View, DetailView, RedirectView, TemplateView
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from storybase.utils import escape_json_for_html, roundrobin
from storybase.views import EmbedView, EmbedPopupView, ShareView, SharePopupView
from storybase.views.generic import ModelIdDetailView, Custom404Mixin, VersionTemplateMixin
from storybase_asset.api import AssetResource
from storybase_asset.models import ASSET_TYPES
from storybase_geo.models import Place
from storybase_help.api import HelpResource
from storybase_messaging.forms import StoryContactMessageForm
from storybase_story.api import (ContainerTemplateResource,
    SectionAssetResource, SectionResource,
    StoryResource, StoryTemplateResource)
from storybase_story.models import (SectionLayout, Story, StoryRelation,
        StoryTemplate)
from storybase_taxonomy.models import Category, Tag
from storybase_badge.models import Badge
from storybase_user.views import Organization, Project


class ExploreStoriesView(TemplateView):
    """
    A view that lets users filter a list of stories

    The heavy lifting is done by ```StoryResource``` and client-side
    JavaScript.

    """
    template_name = "storybase_story/explore_stories.html"

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

    def get_context_data(self, **kwargs):
        resource = StoryResource()
        to_be_serialized = resource.explore_get_data_to_be_serialized(self.request)
        return {
            'stories_json': mark_safe(resource.serialize(None, to_be_serialized,
                                                         'application/json')),
            'selected_filters': mark_safe(json.dumps(self._get_selected_filters())),
        }


class StoryViewerView(ModelIdDetailView):
    context_object_name = "story"
    queryset = Story.objects.not_connected()
    template_name = 'storybase_story/story_viewer.html'

    def get_context_data(self, **kwargs):
        context = super(StoryViewerView, self).get_context_data(**kwargs)
        preview = self.kwargs.get('preview', False)
        referrer = self.request.META.get('HTTP_REFERER', None)
        if referrer:
            try:
                match = resolve(getattr(urlparse.urlparse(referrer), 'path'))
                if match.url_name is 'explore_stories':
                    context['referrer'] = {'caption': _(u"Back to Explorer Results"),
                                           'url': referrer}
                elif match.url_name is 'haystack_search':
                    context['referrer'] = {'caption': _(u"Back to Search Results"),
                                           'url': referrer}
            except Resolver404:
                pass
            except AttributeError:
                pass

        if preview and self.request.user.is_authenticated():
            # Previewing the story in the viewer, include draft
            # related stories belonging to this user
            context['connected_stories'] = self.object.connected_stories(published_only=False, draft_author=self.request.user)
            context['relevant_stories'] = self.object.relevant_stories(published_only=False, draft_author=self.request.user)

        if 'connected_stories' not in context:
            # Viewing the story in the viewer, show only published
            # connected stories
            context['connected_stories'] = self.object.connected_stories()

        if 'relevant_stories' not in context:
            # Viewing the story in the viewer, show only published
            # relevant stories
            context['relevant_stories'] = self.object.relevant_stories()

        context['sections_json'] = self.object.structure.sections_json()

        context['contact_email'] = settings.STORYBASE_CONTACT_EMAIL

        # feedback_form = StoryContactMessageForm(initial={'story': self.object})
        # feedback_form.fields['story'].widget = HiddenInput()
        # context['feedback_form'] = feedback_form
        context['feedback_form'] = StoryContactMessageForm(initial={'story': self.object})

        # Currently supporting two "contexts" in which the viewer lives:
        # iframe and normal
        supported_contexts = ['normal', 'iframe']
        try:
            viewer_context = self.request.REQUEST.get('context', 'normal')
            context['context'] = (viewer_context
                                  if viewer_context in supported_contexts
                                  else 'normal')
        except AttributeError:
            # No self.request defined, default to normal context
            viewer_context = 'normal'

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
        bundle = resource.build_bundle()
        objects = resource.obj_get_list(bundle, story__story_id=story.story_id)
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
            bundle = resource.build_bundle()
            objects = resource.obj_get_list(bundle, section__section_id=section.section_id)
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
        bundle = resource.build_bundle()
        # Set the resource request's user to match this view's
        # request's user.  Otherwise authorization checks won't work
        bundle.request.user = self.request.user
        objects = resource.obj_get_list(bundle, featured=featured,
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
        bundle = resource.build_bundle()
        objects = resource.obj_get_list(bundle)
        bundles = [resource.build_bundle(obj=obj) for obj in objects]
        to_be_serialized['objects'] = [resource.full_dehydrate(bundle) for bundle in bundles]
        return resource.serialize(None, to_be_serialized, 'application/json')

    def get_layouts_json(self):
        to_be_serialized = [{'name': layout.name,
                             'layout_id': layout.layout_id,
                             'slug': layout.slug} for layout
                            in SectionLayout.objects.all()]
        return json.dumps(to_be_serialized, cls=DjangoJSONEncoder)

    def get_asset_types_json(self):
        to_be_serialized = [{'name': asset_type[1], 'type': asset_type[0]} for asset_type in ASSET_TYPES]
        return json.dumps(to_be_serialized)

    def get_help_json(self):
        # Lookup keys to filter help items to include
        help_slugs = ['story-information', 'call-to-action', 'new-section']
        to_be_serialized = {}
        resource = HelpResource()
        bundle = resource.build_bundle()
        objects = resource.obj_get_list(bundle).filter(slug__in=help_slugs)
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
        return json.dumps(to_be_serialized, cls=DjangoJSONEncoder)

    def get_organizations_json(self):
        to_be_serialized = [{'organization_id': org.organization_id,
                             'name': org.name}
                            for org in self.request.user.organizations.all()]
        return json.dumps(to_be_serialized, cls=DjangoJSONEncoder);

    def get_projects_json(self):
        # TODO: Update this to include "Open Projects"
        to_be_serialized = [{'project_id': project.project_id,
                             'name': project.name}
                            for project in self.request.user.projects.all()]
        return json.dumps(to_be_serialized, cls=DjangoJSONEncoder);

    def get_related_stories_json(self):
        """
        Return a JSON representation of the stories related stories
        to bootstrap Backbone views
        """
        if self.object:
            # Existing story, return a representation of the related stories
            q = Q(source=self.object) | Q(target=self.object)
            return json.dumps({
                'objects': [
                  {
                      'source': rel.source.story_id,
                      'target': rel.target.story_id,
                      'target_title': rel.target.title,
                      'target_url': rel.target.get_absolute_url(),
                      'relation_type': rel.relation_type,
                  }
                  for rel in StoryRelation.objects.filter(q)
                ]
            }, cls=DjangoJSONEncoder)
        elif self.source_story:
            # New connected story, bootstrap the Backbone view with
            return json.dumps({
                'objects': [
                    {
                        'source': self.source_story.story_id,
                        'relation_type': 'connected'
                    },
                ]
            }, cls=DjangoJSONEncoder)
        else:
            # New non-connected story, no connected stories.
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
        bundle = resource.build_bundle()
        objects = resource.obj_get_list(bundle,
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
                'info': True,
                'tag': True,
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
            'previewURLTemplate': '/stories/{{story_id}}/preview/',
            # Template for generating view URLs
            'viewURLTemplate': '/stories/{{slug}}/viewer/',
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
                'previewURLTemplate': '/stories/%s/preview/#connected-stories/{{story_id}}' % (self.source_story.story_id),
                'viewURLTemplate': '/stories/%s/viewer/#connected-stories/{{story_id}}' % (self.source_story.story_id),
            })
        return json.dumps(options)

    def get_context_data(self, **kwargs):
        """Bootstrap data for Backbone models and collections"""
        context = {
            'asset_types_json': mark_safe(self.get_asset_types_json()),
            'help_json': mark_safe(escape_json_for_html(
                self.get_help_json())),
            'layouts_json': mark_safe(self.get_layouts_json()),
            'organizations_json': mark_safe(self.get_organizations_json()),
            'places_json': mark_safe(self.get_places_json()),
            'projects_json': mark_safe(self.get_projects_json()),
            'story_template_json': mark_safe(self.get_story_template_json()),
            'topics_json': mark_safe(self.get_topics_json()),
        }

        if self.object:
            context['story'] = self.object
            context['story_json'] = mark_safe(self.get_story_json())
            context['featured_assets_json'] = mark_safe(escape_json_for_html(
                self.get_assets_json(featured=True)))
            context['assets_json'] = mark_safe(escape_json_for_html(
                self.get_assets_json()))
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

        if (self.template_object and self.template_object.slug == settings.STORYBASE_CONNECTED_STORY_TEMPLATE):
            context['show_story_info_inline'] = True

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


LANG_PREFIX_RE = re.compile(r"^/(%s)/" % "|".join([re.escape(lang[0]) for lang in settings.LANGUAGES]))

class StoryWidgetView(Custom404Mixin, VersionTemplateMixin, DetailView):
    """
    An embedable widget for a story or list of stories

    This view allows stories or lists of stories to be embedded in a page on an
    external site.  It is designed to to be rendered inside an iframe by adding
    the ``widgets.min.js`` script to a page.

    **Context**

    * ``object``: In a story list widget, this will be model for the taxonomy
       term. In a story widget, or a story + list widget, this will be the
       primary story for the widget.
    * ``taxonomy_terms``: A list of models for taxonomy items (organizations,
       projects, etc) related to the widget content
    * ``story``: The primary story for the widget
    * ``stories``: Optional list of related stories

    **Template**

    * ``storybase_story/widget_base.html``: Base template containing all of
      the markup for the widget.  All other widget templates inherit from this
      template.
    * ``storybase_story/widget_story.html``: Template for widget display that
      only shows a single story.
    * ``storybase_story/widget_storylist.html``: Template for widget that
      displays a list of stories.
    * ``storybase_story/widget_story_storylist.html``: Template for widget that
      displays a featured story and a list of stories.
    * ``storybase_story/widget_404.html``: Template when URL passed to the
      view cannot be resolved.

    """

    # A map of URL names from a URL pattern for a taxonomy term view to
    # the queryset, lookup fields and relationship field of the Story model
    url_name_lookup = {
        'story_viewer': {
            'queryset': Story.objects.published(),
            'lookup_fields': {
                'slug': 'slug',
                'story_id': 'story_id',
            },
        },
        'organization_detail': {
            'queryset': Organization.objects.published(),
        },
        'project_detail': {
            'queryset': Project.objects.published(),
        },
        'tag_stories': {
            'queryset': Tag.objects.all(),
            'related_field': 'tags',
        },
        'topic_stories': {
            'queryset': Category.objects.all(),
            'lookup_fields': {'slug': 'categorytranslation__slug'},
            'related_field': 'topics',
        },
        'place_stories': {
            'queryset': Place.objects.all(),
        },
    }

    def get(self, request, *args, **kwargs):
        # Try to resolve the URLs past as the list-url and story-url GET
        # parameters.  These will be used to get the context object and
        # stories later
        self.list_url = self.request.GET.get('list-url', None)
        self.story_url = self.request.GET.get('story-url', None)
        self.list_match = self.resolve_uri(self.list_url) if self.list_url else None
        self.story_match = self.resolve_uri(self.story_url) if self.story_url else None
        return super(StoryWidgetView, self).get(request, *args, **kwargs)

    def get_template_names(self):
        """
        Returns a list of template names to search for when rendering the template.

        Includes one of:

        - widget_story.html
        - widget_storylist.html
        - widget_story_storylist.html

        For each case of story, list, or story+list. Includes 404 if something
        went wrong and we have a match for neither story nor list.

        It will also include versioned template names if a ``version`` argument
        was passed to the view.

        """
        template_names = []
        if self.story_match and self.list_match:
            template_names.append('storybase_story/widget_story_storylist.html')
        elif self.story_match and not self.list_match:
            template_names.append('storybase_story/widget_story.html')
        elif not self.story_match and self.list_match:
            template_names.append('storybase_story/widget_storylist.html')
        else:
            template_names.append('storybase_story/widget_404.html')

        version = self.kwargs.get('version', None)
        if version is not None:
            # If a version was included in the keyword arguments, search for a
            # version-specific template first
            template_names = self.get_versioned_template_names(template_names, version)

        return template_names

    def get_404_template_name(self):
        return "storybase_story/widget_404.html"

    def resolve_uri(self, uri):
        """
        Resolve a full URL

        This is a wrapper around ``django.core.urlresolvers.reverse()`` that
        first strips the non-path URL parts.

        Returns a ``ResolverMatch`` object or None if there is no match
        """
        prefix = get_script_prefix()
        parsed = urlparse.urlparse(uri)
        path = parsed.path
        chomped_path = path

        if prefix and chomped_path.startswith(prefix):
            chomped_path = chomped_path[len(prefix)-1:]

        if chomped_path[-1] != '/':
            chomped_path += '/'

        # If the language isn't in the path, add it, otherwise resolve() will
        # fail
        if not LANG_PREFIX_RE.match(chomped_path):
            chomped_path = "/%s%s" % (settings.LANGUAGE_CODE, chomped_path)

        try:
            match = resolve(chomped_path)
        except Http404:
            return None

        if match.url_name not in self.url_name_lookup:
            return None

        return match

    def get_object_match(self):
        """
        Return the ResolverMatch object that will be used to retrieve
        the primary object displayed by the view
        """
        if self.story_match:
            return self.story_match
        elif self.list_match:
            return self.list_match
        else:
            raise Http404

    def get_related_field_name(self, match):
        """
        Return the relationship field of the Story model for a particular view
        """
        query_info = self.url_name_lookup[match.url_name]
        try:
            return query_info['related_field']
        except KeyError:
            return force_text(query_info['queryset'].model._meta.verbose_name_plural)

    def get_filter_kwargs(self, match, related_field_name=None):
        """
        Get a dictionary of arguments to filter the object or story queryset
        """
        try:
            lookup_fields = self.url_name_lookup[match.url_name]['lookup_fields']
        except KeyError:
            lookup_fields = {'slug': 'slug'}

        for kwarg, model_field_name in lookup_fields.items():
            if kwarg in match.kwargs:
                # If the query field is on a related model, prepend the
                # relationship field name
                field_name = model_field_name
                if related_field_name:
                    field_name = "%s__%s" % (related_field_name, field_name)
                return {
                    field_name: match.kwargs[kwarg]
                }

        raise AttributeError

    def get_queryset(self):
        try:
            return self.url_name_lookup[self.get_object_match().url_name]['queryset']
        except KeyError:
            raise Http404

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        filter_kwargs = self.get_filter_kwargs(self.get_object_match())
        queryset = queryset.filter(**filter_kwargs)

        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def get_story_taxonomy_terms(self, story, n_items=3):
        """
        Return a list of taxonomy term models related to the widget's
        primary story.

        Interleave a list of mixed results, but containing no more than ``n_items``
        items total.
        """
        return list(roundrobin(story.organizations.all(), story.projects.all()))[:n_items]

    def get_context_data(self, **kwargs):
        """
        Returns context data for displaying the story and an optional list of
        related stories

        The view accepts an optional ``list-url`` query string parameter.
        This parameter should be the full URL of a page for an organization,
        project, place, keyword (tag) or topic (category). If this parameter is
        present, the widget output will also contain a list of recent stories
        from that taxonomy item.

        """
        # Calling super sets context['object']
        context = super(StoryWidgetView, self).get_context_data(**kwargs)
        context['stories'] = []

        if self.list_match:
            filter_kwargs = self.get_filter_kwargs(self.list_match, self.get_related_field_name(self.list_match))
            context['stories'] = Story.objects.published().filter(**filter_kwargs).order_by('-published')[:3]
            # This is a list widget. The taxonomy sole taxonomy term is the term
            # we're displaying in the widget
            context['taxonomy_terms'] = [context['object']]

        if 'story' in context:
            # This is a story-only view. Get the related taxonomy models for the
            # story
            context['taxonomy_terms'] = self.get_story_taxonomy_terms(context['story'])


        return context


class StoryListView(MultipleObjectMixin, ModelIdDetailView):
    """
    Base view class for a list of stories aggregated by an organization,
    project, place, keyword (tag) or topic (category)
    """
    template_name = "storybase_story/story_list.html"
    paginate_by = 10

    def get_related_field_name(self):
        """
        Returns the relationship field name

        Returns the name of the field of the Story model that defines the
        relationship with the model used to aggregate the stories.

        Defaults to the ``related_field_name`` attribute of the view class

        """
        return self.related_field_name

    def get_slug_field_name(self):
        """
        Returns the name of the slug field on the related model
        """
        return 'slug'

    def get_story_filter_kwargs(self):
        filter_kwargs = {}
        slug_field_name = self.get_slug_field_name()
        related_field_name = self.get_related_field_name()
        if 'slug' in self.kwargs:
            filter_kwargs['%s__%s' % (related_field_name, slug_field_name)] = self.kwargs['slug']
        else:
            # While the likely lookup field is "slug", also support filtering by
            # model ID (e.g. "project_id")
            model_id = None
            try:
                related_field = getattr(Story, related_field_name).field
                model_name = related_field.model._meta.model_name
                model_id = '%s_id' % model_name
            except AttributeError:
                pass

            if model_id and model_id in self.kwargs:
                filter_kwargs['%s__%s' % (related_field_name, model_id)] = self.kwargs[model_id]
            else:
                raise AttributeError

        return filter_kwargs

    def get_context_data(self, **kwargs):
        """
        Returns context data for displaying the list of stories

        **Context**

        * ``object``: Model instance of item used to aggregate stories
        * ``object_list``: List of stories
        * ``stories``: An alias for ``object_list``
        * ``is_paginated``: A boolean representing whether the results are paginated. Specifically, this is set to False if no page size has been specified, or if the available objects do not span multiple pages.
        * ``paginator``: An instance of django.core.paginator.Paginator. If the page is not paginated, this context variable will be None.
        * ``page_obj``: An instance of django.core.paginator.Page. If the page is not paginated, this context variable will be None.

        """
        context = super(ModelIdDetailView, self).get_context_data(**kwargs)
        paginator = None
        page = None
        is_paginated = False
        filter_kwargs = self.get_story_filter_kwargs()
        queryset = Story.objects.published().filter(**filter_kwargs).order_by('-published')

        page_size = self.get_paginate_by(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)

        context.update({
            'paginator': paginator,
            'page_obj': page,
            'is_paginated': is_paginated,
            'object_list': queryset,
            'stories': queryset,
        })

        return context


# TODO: Figure out semantics and behavior for explorer that allows filtering
# via URL path parameters, e.g. /explore/projects/<project-slug>/
# The biggest question I have about this is whether we should allow re-filtering
# of term filtered by the path parameter
class ExplorerRedirectView(RedirectView):
    """
    Base view that redirects to the explorer view
    """
    permanent = False

    def get_query_string(self, **kwargs):
        """
        Returns query string to filter

        This should be overridden in a sub-class to translate a URL path
        parameter (likely "slug") to a filter query argument of the explore
        view.

        """
        return None

    def get_redirect_url(self, **kwargs):
        """
        Constructs a URL to a filtered version of the explore view
        """
        url = reverse('explore_stories')
        args = self.get_query_string(**kwargs)
        if args:
            url = "%s?%s" % (url, args)
        return url


class StorySharePopupView(SharePopupView):
    """
    Popup content for sharing a story
    """
    queryset = Story.objects.published()


class StoryShareView(ShareView):
    queryset = Story.objects.published()


class StoryEmbedPopupView(EmbedPopupView):
    """
    Popup content for embedding a story
    """
    queryset = Story.objects.published()


class StoryEmbedView(EmbedView):
    queryset = Story.objects.published()
