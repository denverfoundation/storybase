"""Interpret a story and render its structure"""
from django.utils.safestring import mark_safe

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

    def __init__(self, story):
        self.story = story

    def render_toc(self, format='html'):
        """Return a rendered table of contents for a story"""
        raise NotImplemented


class SpiderStructure(BaseStructure):
    """A story structure that drills down from a central concept"""
    name = 'Spider'
    id = 'spider'

    def render_toc(self, format='html', **kwargs):
        """Return a rendered table of contents for a story"""
        # TODO: Perhaps its better to implement this with templates/
        # template tags, or put this functionality in the Backbone app
        def render_toc_section(section):
            output = []
            output.append("<li>")
            output.append("<a href='#sections/%s'>%s</a>" %
                          (section.section_id, section.title))
            if section.is_root():
                output.append("<ul>")
                for child in section.children.order_by('weight'):
                    output.append(render_toc_section(child))
                output.append("</ul>")
            output.append("</li>")
            return u'\n'.join(output)

        html_class = kwargs.get('html_class', None)
        output = []
        html_class_str = ''
        if html_class is not None:
            html_class_str = " class='%s'" % html_class
        output.append("<ul%s>" % html_class_str)
        for root_section in self.story.sections.filter(root=True) \
                                               .order_by('weight'):
            output.append(render_toc_section(root_section))
        output.append("</ul>")
        return mark_safe(u'\n'.join(output))


class LinearStructure(BaseStructure):
    """A story structure intended to be read top-to-bottom"""
    name = 'Linear'
    id = 'linear'

    def render_toc(self, format='html', **kwargs):
        """Return a rendered table of contents for a story"""
        # TODO: Perhaps its better to implement this with templates/
        # template tags, or put this functionality in the Backbone app
        def render_toc_section(section):
            output = []
            output.append("<li><a href='#sections/%s'>%s</a></li>" %
                          (section.section_id, section.title))
            for child in section.children.order_by('weight'):
                output.append(render_toc_section(child))
            return u'\n'.join(output)

        html_class = kwargs.get('html_class', None)
        output = []
        html_class_str = ''
        if html_class is not None:
            html_class_str = " class='%s'" % html_class
        output.append("<ul%s>" % html_class_str)
        for root_section in self.story.sections.filter(root=True) \
                                               .order_by('weight'):
            output.append(render_toc_section(root_section))
        output.append("</ul>")
        return mark_safe(u'\n'.join(output))

manager = StructureManager()
manager.register(SpiderStructure)
manager.register(LinearStructure)

DEFAULT_STRUCTURE = LinearStructure.id
