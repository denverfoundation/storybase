"""Views for storybase_story app"""

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, render
from django.template import Context
from django.template.loader import get_template
from django.utils import translation
#from django.views.generic import DetailView
from storybase_story.models import Story

# TODO: Use this if we decide not to use the redirect-based language system
#class StoryDetailView(DetailView):
#    context_object_name = "story"
#    queryset = Story.objects.all()
#
#    def get_object(self):
#        object = self.queryset.get(story_id=self.kwargs['story_id'])
#        return object

def simple_story_list(stories):
    """Render a simple listing of stories
    
    Arguments:
    stories -- A queryset of Story model instances

    """
    template = get_template('storybase_story/simple_story_list.html')
    # TODO: Implement this template
    context =  Context({"stories": stories})
    return template.render(context)

def homepage_story_list():
    """Render a listing of stories for the homepage"""
    stories = Story.objects.on_homepage().order_by('-last_edited')
    return simple_story_list(stories)

def story_detail(request, **kwargs):
    """Display metadata, assets and structure of a Story"""
    try:
        language_code = translation.get_language()
	story_id = kwargs.get('story_id', None)
	slug = kwargs.get('slug', None)
	if slug is not None:
	    story = Story.objects.get(slug=kwargs['slug'])
	elif story_id is not None:
	    story = Story.objects.get(story_id=kwargs['story_id'])
	else:
	    raise AssertionError("story_detail view must be called with either "
			         "a object story_id or slug")
	    
        available_languages = story.get_languages()
        if language_code not in available_languages:
            alt_lang = settings.LANGUAGE_CODE
            if alt_lang not in available_languages:
                alt_lang = available_languages[0]
            path = story.get_absolute_url()
            return redirect('/%s%s' % (alt_lang, path))
    except Story.DoesNotExist:
        raise Http404
    return render(request, 'storybase_story/story_detail.html', 
                  {'story': story})
