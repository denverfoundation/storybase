from lettuce import step, world
from nose.tools import assert_in
from splinter.exceptions import ElementDoesNotExist
from storybase_story.models import Story
from storybase_user.models import Project, ProjectStory

def find_last_projectstory_form():
    return world.browser.find_by_css('.dynamic-projectstory_set').last

@step(u'Given the user selects the Story "([^"]*)" from the drop-down menu')
def selects (step, title):
    projectstory_form = find_last_projectstory_form()
    world.select_option_by_text("%s-story" % projectstory_form['id'], title)

@step(u'Then the Project\'s featured story should be "([^"]*)"')
def see_featured_story(step, name):
    world.browser.is_element_present_by_css('.featured-story')
    featured_text = world.browser.find_by_css('.featured-story').first.text
    assert_in(name, featured_text)

@step(u'Then the Project\'s stories list should list these stories')
def see_stories_list(step):
    story_titles = [row['title'] for row in step.hashes]
    world.assert_list_equals('.story-list li h4', story_titles)

@step(u'Given the user sets the weight of Story "([^"]*)" to "([^"]*)"')
def change_story_weight(step, title, weight):
    for projectstory_form in world.browser.find_by_css('.dynamic-projectstory_set'):
        projectstory_id = projectstory_form['id']
        if world.option_selected_by_text("%s-story" % projectstory_id, title):
            world.browser.fill("%s-weight" % projectstory_id, weight)
            return True

    raise ElementDoesNotExist, "Could not find associated story with title %s" % title

@step(u'Given the user removes the Story "([^"]*)" from the Project')
def remove_story(step, title):
    for projectstory_form in world.browser.find_by_css('.dynamic-projectstory_set'):
        projectstory_id = projectstory_form['id']
        if world.option_selected_by_text("%s-story" % projectstory_id, title):
            world.browser.check("%s-DELETE" % projectstory_id)
            return True

    raise ElementDoesNotExist, "Could not find associated story with title %s" % title

@step(u'Given the Story "([^"]*)" is the featured story for the Project "([^"]*)"')
def project_featured_story(step, story_title, project_name):
    story = Story.objects.get(storytranslation__title=story_title)
    project = Project.objects.get(projecttranslation__name=project_name)
    try:
        ps = ProjectStory.objects.get(story=story, project=project)
    except ProjectStory.DoesNotExist:
        ps = ProjectStory.objects.create(story=story, project=project,
            weight=0)
