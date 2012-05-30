from storybase.managers import FeaturedManager

class StoryManager(FeaturedManager):
    def on_homepage(self):
        """Return items to be featured on homepage"""
        return super(StoryManager).on_homepage().filter(status='published')
