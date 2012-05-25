import re

from storybase_user.models import Organization, Project
from storybase_geo.models import Location, Place
from storybase_story.models import create_story
from storybase_taxonomy.models import Category

def bulk_create(hashes):
    """Bulk create stories from a list of dictionaries

    This is meant to be passed a csv.DictWriter object or steps.hashes in a
    lettuce step

    Arguments:
    hashes -- List of dictionaries containing story attributes

    """
    def _nonempty(names):
        return [name for name in names if name]

    def _parse_names(names):
        return _nonempty(re.split(',\W+', names))

    for story_dict in hashes:
        title = story_dict['title']
        summary = story_dict['summary']
        byline = story_dict['byline']
        org_names = _parse_names(story_dict['organizations'])
        proj_names = _parse_names(story_dict['projects'])
        topic_names = _parse_names(story_dict['topics'])
        place_names = _parse_names(story_dict['places'])
        loc_names = _parse_names(story_dict['locations'])
        orgs = list(Organization.objects.filter(organizationtranslation__name__in=org_names))
        projects = list(Project.objects.filter(projecttranslation__name__in=proj_names))
        topics = list(Category.objects.filter(categorytranslation__name__in=topic_names))
        places = list(Place.objects.filter(name__in=place_names))
        locations = list(Location.objects.filter(name__in=loc_names))
        story = create_story(title=title, summary=summary, byline=byline,
                             status='published')
        story.organizations.add(*orgs)
        story.projects.add(*projects)
        story.topics.add(*topics)
        story.places.add(*places)
        story.locations.add(*locations)
        story.save()
