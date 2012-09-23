import re

from django.conf import settings

from storybase_user.models import Organization, Project
from storybase_geo.models import Location, Place
from storybase_story.models import (Container, SectionAsset, SectionLayout,
    create_section, create_story, create_story_template)
from storybase_taxonomy.models import Category
from storybase_asset.models import (create_external_asset, create_html_asset)

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

def create_connected_story_template():
    """
    Create the connected stories template

    This is essentially a programatic fixture for creating the 
    connected story template
    """
    story = create_story(title="Connected Story Template", language="en",
                         status="published", is_template=True)
    layout = SectionLayout.objects.get(sectionlayouttranslation__name="Side by Side")
    section = create_section(title="Photo and Image", language="en",
        story=story, layout=layout)
    asset1 = create_external_asset(title="Mock Image Asset", type='image',
        url='http://exampledomain.com/fake.png')
    asset2 = create_html_asset(title="Mock Text Asset", type='text')
    left = Container.objects.get(name='left')
    right = Container.objects.get(name='right')
    SectionAsset.objects.create(section=section, asset=asset1, container=left)
    SectionAsset.objects.create(section=section, asset=asset2, container=right)
    return create_story_template(title="Connected Story", story=story,
        slug=settings.STORYBASE_CONNECTED_STORY_TEMPLATE)
