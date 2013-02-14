import random
from django.db.models import Count
from django.template.loader import render_to_string
from storybase_story.models import Story
from storybase_taxonomy.models import Category

class BannerRegistry(object):
    _banner_classes = {}

    def register_banner(self, banner_cls):
        self._banner_classes[banner_cls.banner_id] = banner_cls

    def get_banner(self, banner_id, **kwargs):
        return self._banner_classes[banner_id](**kwargs)

    def get_random_banner(self, **kwargs):
        banner_id = random.choice(self._banner_classes.keys())
        return self.get_banner(banner_id, **kwargs)


class Banner(object):
    """
    Base class for banner implementations.

    In most cases, just override get_objects in the subclass to use a 
    different strategy for selecting stories.

    """
    template_name = "storybase_story/banner.html"
    # TODO: Decide on real value for this default 
    img_width = 335

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    # Using "objects" instead of "stories" to anticipate including other
    # things (projects, organizations, users) in banner one day.
    def get_objects(self, count=10):
        # TODO: This code is repeated a lot.  Maybe it needs to be in
        # a custom manager?
        return Story.objects.filter(status='published')[:count]

    def get_context_data(self):
        return {
            'objects': [o.normalize_for_view(img_width=self.img_width)
                        for o in self.get_objects()],
        }

    def render(self):
        # TODO: Cache output
        rendered = render_to_string(self.template_name, self.get_context_data())
        return rendered

# TODO: Exclude connected stories from these, I think by using a custom
# manager

class RandomBanner(Banner):
    """
    Banner that shows randomly selected stories

    """
    banner_id = "random"

    def get_objects(self, count=10):
        # Sort the objects randomly. Unfortunately, we can't use call 
        # the parent's get_objects because QuerySets can't be reordered
        # after being sliced.
        return Story.objects.filter(status='published').order_by('?')[:count]


class TopicBanner(Banner):
    """
    Banner that selects stories with a specified topic.
    """
    banner_id = "topic"

    def get_random_topic(self, count):
        # Limit elgible topics to only those with at least ``count``
        # associated stories
        topics = Category.objects.filter(stories__status='published')\
                         .annotate(num_stories=Count('stories'))\
                         .filter(num_stories__gte=count)
        if not topics.count():
            # No topics with stories
            return None

        return topics[0]
        
    def get_objects(self, count=10):
        slug = getattr(self, 'slug', None)
        if slug is None:
            topic = self.get_random_topic(count) 
        else:
            topic = Category.objects.get(categorytranslation__slug=slug)

        if not topic:
            # No eligible topic, return an empty list
            return []

        # Return all the stories
        return topic.stories.filter(status='published').order_by('?')[:count]
        

# Create a single instance of BannerRegistry for import elsewhere
registry = BannerRegistry()

# Register our banner implementations
registry.register_banner(RandomBanner)
registry.register_banner(TopicBanner)
