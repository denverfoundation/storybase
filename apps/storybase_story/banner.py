import random

from django.template.loader import render_to_string
from storybase_story.models import Story

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

class RandomBanner(Banner):
    banner_id = "random"

    def get_objects(self, count=10):
        # Sort the objects randomly. Unfortunately, we can't use call 
        # the parent's get_objects because QuerySets can't be reordered
        # after being sliced.
        return Story.objects.filter(status='published').order_by('?')[:count]


registry = BannerRegistry()
registry.register_banner(RandomBanner)
