from django.template.loader import render_to_string
from storybase_story.models import Story

# Old code, just for reference
#def homepage_banner_list(num_stories):
#    """Render a listing of stories for the homepage banner """
#    # temp -- just putting out demo images
#    #stories = Story.objects.on_homepage().order_by('-last_edited')[:num_stories]
#    stories = []
#    image_num = 1
#    for i in range(num_stories):
#        image_num = i + 1
#        if (image_num > 9):
#            image_num -= 9
#        stories.append({"image": "image%d.jpg" % image_num, "title": "banner story %d title here." % i})
#    return stories

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
    def get_objects(self, count=10):
        # Sort the objects randomly. Unfortunately, we can't use call 
        # the parent's get_objects because QuerySets can't be reordered
        # after being sliced.
        return Story.objects.filter(status='published').order_by('?')[:count]


# TODO: Registration of banner classes
