from lettuce import before, step, world

@before.each_scenario
def setup(scenario):
    matching_scenarios = ('Associate multiple stories to a project',)
    if scenario.name in matching_scenarios: 
        world.create_project('The Metro Denver Regional Equity Atlas')
        story_summary = """
            Many families in the Denver metro area use public
            transportation instead of a school bus because for them, a
            quality education is worth hours of daily commuting. Colorado's
            school choice program is meant to foster educational equity,
            but the families who benefit most are those who have time and
            money to travel. Low-income families are often left in a lurch.
            """
        world.create_story(title='Transportation Challenges Limit Education Choices for Denver Parents', summary=story_summary)
        world.create_story(title='Connecting the Dots Between Transit And Other Regional Priorities')

def find_last_projectstory_form():
    return world.browser.find_by_css('.dynamic-projectstory_set').last

@step(u'Given the user selects the Story "([^"]*)" from the drop-down menu')
def selects (step, title):
    projectstory_form = find_last_projectstory_form()
    world.select_option_by_text("%s-story" % projectstory_form['id'], title)

@step(u'Then the Project\'s stories list should list these stories')
def see_stories_list(step):
    story_titles = [row['title'] for row in step.hashes]
    world.assert_list_equals('ul.stories li', story_titles)
