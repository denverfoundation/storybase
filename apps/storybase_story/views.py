from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import translation
#from django.views.generic import DetailView
from models import Story

# TODO: Use this if we decide not to use the redirect-based language system
#class StoryDetailView(DetailView):
#    context_object_name = "story"
#    queryset = Story.objects.all()
#
#    def get_object(self):
#        object = self.queryset.get(story_id=self.kwargs['story_id'])
#        return object

def story_detail(request, **kwargs):
    try:
        language_code = translation.get_language()
        print language_code
        story = Story.objects.get(story_id = kwargs['story_id'])
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
