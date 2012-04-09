"""Interpret a story and render its structure"""

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

    def get_toc(self):
        """Return an object representing the table of contents"""
        raise NotImplemented

    def render_toc(self, format='html'):
        """Return a rendered table of contents for a story"""
        raise NotImplemented


class SpiderStructure(BaseStructure):
    """A story structure that drills down from a central concept"""
    name = 'Spider'
    id = 'spider'


class LinearStructure(BaseStructure):
    """A story structure intended to be read top-to-bottom"""
    name = 'Linear'
    id = 'linear'

manager = StructureManager()
manager.register(SpiderStructure)
manager.register(LinearStructure)

DEFAULT_STRUCTURE = LinearStructure.id
