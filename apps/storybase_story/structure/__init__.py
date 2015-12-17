"""Interpret a story and render its structure"""
import json
from uuid import UUID

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from storybase.utils import open_html_element, close_html_element


class StructureManager(object):
    def __init__(self):
        self._registry = {}

    def register(self, structure_class):
        """Register a story structure with the manager"""
        self._registry[structure_class.id] = structure_class

    def get_structure_class(self, id):
        """Get a structure class with the given id"""
        return self._registry[id]

    def get_structure_options(self):
        """
        Get the registered structures in a format appropriate for the
        options parameter of a Django model field
        """
        return [(id, klass.name) for id, klass
                in self._registry.iteritems()]


class BaseStructure(object):
    """Base class for a story structure"""
    name = ''
    """The human-readable name of the story structure"""
    id = ''
    """A machine name for the story structure"""
    story = None
    """A Story model instance"""
    _sections_flat = []
    _previous_sections = {}
    _next_sections = {}

    def _section_children_flat(self, section):
        """
        Return a list of child sections ordered with each branch
        coming before the next. Also make a note of the next section as
        we traverse the sections.
        """
        section_children_flat = []
        previous = None
        for child_relation in section.child_relations():
            child = child_relation.child
            section_children_flat.append(child)
            if previous is None:
                # First child section
                self._previous_sections[child] = section
            else:
                self._previous_sections[child] = previous
                self._next_sections[previous] = child

            children_flat = self._section_children_flat(child)
            if len(children_flat) > 0:
                section_children_flat = (section_children_flat +
                                         children_flat)
                # The next section is the first child
                self._next_sections[child] = children_flat[0]
                # The next section's previous will be the last child
                previous = children_flat[-1]
            else:
                previous = child
                self._next_sections[child] = None

        return section_children_flat

    def __init__(self, story):
        self.story = story
        self._sections_flat = []
        self._previous_sections = {}
        self._next_sections = {}
        # Build a representation of the sections flattened and
        # of the next and previous section for a given section
        root_sections = self.story.sections.filter(root=True) \
                                           .order_by('weight')

        previous = None
        for section in root_sections:
            self._sections_flat.append(section)
            self._previous_sections[section] = previous
            if previous is not None:
                self._next_sections[previous] = section

            children = self._section_children_flat(section)
            if len(children) > 0:
                self._sections_flat = self._sections_flat + children
                self._next_sections[section] = children[0]
                previous = children[-1]
            else:
                # Set the next section for the current section to None
                # This will get overridden with the actual next section
                # if the loop runs again
                self._next_sections[section] = None
                previous = section

    @property
    def sections_flat(self):
        return self._sections_flat

    def sections(self, include_summary=True, include_call_to_action=True,
                 connected_stories=None):
        """Return a simple representation of the story sections

        This representation doesn't include the content of sections, just
        their titles, IDs and the relationship with other sections.

        Keyword arguments:
        include_summary -- Include the story summary as the first section
                           (default True)
        include_call_to_action -- Include the call to action as the last
                                  section (default True)

        """
        if connected_stories is None:
            connected_stories = self.story.connected_stories()
        sections = []
        for section in self._sections_flat:
            sections.append(section.to_simple())

        if include_summary and self.story.summary:
            summary_section = {
                   'section_id': 'summary',
                   'title': _("Summary"),
                   'children': [],
                   'next_section_id': (sections[0]['section_id']
                                       if len(sections) else None)
            }
            if len(sections):
               sections[0]['previous_section_id'] = 'summary'
            sections.insert(0, summary_section)

        if (include_call_to_action and
                (self.story.call_to_action or self.story.allow_connected)):
            call_to_action_section = {
                'section_id': 'call-to-action',
                'title': _("How Can You Help?"),
                'children': [],
                'previous_section_id': (sections[-1]['section_id']
                                        if len(sections) else None)
            }
            if len(sections):
                sections[-1]['next_section_id'] = 'call-to-action'
            sections.append(call_to_action_section)

            if self.story.allow_connected and connected_stories:
                connected_stories_section = {
                    'section_id': 'connected-stories',
                    'title': _("Connected Stories"),
                    'children': [],
                    'previous_section_id': sections[-1]['section_id'],
                }
                sections[-1]['next_section_id'] = 'connected-stories'
                sections.append(connected_stories_section)

        return sections

    def sections_json(self, include_summary=True, include_call_to_action=True,
                      connected_stories=None):
        """Return a JSON representation of the story sections

        This is useful for calling from templates to bootstrap a Backbone
        collection.

        """
        sections = self.sections(include_summary, include_call_to_action,
                                 connected_stories)
        return mark_safe(json.dumps(sections, cls=DjangoJSONEncoder))

    def get_next_section(self, section):
        return self._next_sections[section]

    def get_previous_section(self, section):
        return self._previous_sections[section]

    def call_to_action_toc_link(self):
        """Return a link to the call to action section in the viewer"""
        return "<a href=\"#sections/call-to-action\">%s</a>" % _("How Can You Help?")

    def summary_toc_link(self):
        """Return a link to the summary section in the viewer"""
        return "<a href=\"#sections/summary\">%s</a>" % _("Summary")

    def connected_toc_link(self):
        """Return a link to the connected stories section in the viewer"""
        return "<a href=\"#sections/connected-stories\">%s</a>" % _("Connected Stories")

    def render_toc(self, format='html', **kwargs):
        """Return a rendered table of contents for a story"""
        # TODO: Perhaps its better to implement this with templates/
        # template tags, or put this functionality in the Backbone app
        container_el = kwargs.get('container_el', 'ul')
        container_attrs = kwargs.get('container_attrs', {'class': 'story-toc'})
        item_el = kwargs.get('item_el', 'li')
        item_attrs = kwargs.get('item_attrs', {})

        output = []
        output.append(open_html_element(container_el, container_attrs))
        if self.story.summary:
            output.append("%s%s%s" % (
                          open_html_element(item_el, item_attrs),
                          self.summary_toc_link(),
                          close_html_element(item_el)))
        for section_index, root_section in enumerate(self.story.sections.filter(root=True) \
                                               .order_by('weight'), start=1):
            output.append(self.render_toc_section(root_section, index=section_index))
        if self.story.call_to_action:
            output.append("%s%s%s" % (
                          open_html_element(item_el, item_attrs),
                          self.call_to_action_toc_link(),
                          close_html_element(item_el)))
        if self.story.allow_connected and self.story.connected_stories:
            output.append("<li>%s</li>" % self.connected_toc_link())
        output.append(close_html_element(container_el))

        return mark_safe(u'\n'.join(output))


class SpiderStructure(BaseStructure):
    """A story structure that drills down from a central concept"""
    name = 'Spider'
    id = 'spider'

    def render_toc_section(self, section, **kwargs):
        container_el = kwargs.get('container_el', 'ul')
        container_attrs = kwargs.get('container_attrs', {})
        item_el = kwargs.get('item_el', 'li')
        item_attrs = kwargs.get('item_attrs', {})
        output = []
        output.append(open_html_element(item_el, item_attrs))
        output.append("<a href='#sections/%s'>%s</a>" %
                      (section.section_id, section.title))
        if section.children.count():
            output.append(open_html_element(container_el))
            for child in section.children.order_by('weight'):
                output.append(self.render_toc_section(child, **kwargs))
            output.append(close_html_element(container_el))
        output.append(close_html_element(item_el))
        return u'\n'.join(output)



class LinearStructure(BaseStructure):
    """A story structure intended to be read top-to-bottom"""
    name = 'Linear'
    id = 'linear'

    def render_toc_section(self, section, **kwargs):
        item_el = kwargs.get('item_el', 'li')
        item_attrs = kwargs.get('item_attrs', {})
        section_index = kwargs.get('index', 0)
        output = []
        title = section.title if section.title else "%s %d" % (_("Section"), section_index)
        output.append("%s<a href='#sections/%s'>%s</a>%s" % (
                      open_html_element(item_el, item_attrs),
                      section.section_id, title,
                      close_html_element(item_el)))
        for child in section.children.order_by('weight'):
            output.append(self.render_toc_section(child, **kwargs))
        return u'\n'.join(output)


manager = StructureManager()
manager.register(SpiderStructure)
manager.register(LinearStructure)

DEFAULT_STRUCTURE = LinearStructure.id
