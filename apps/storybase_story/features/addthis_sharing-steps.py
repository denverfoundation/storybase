from lettuce import step, world

from nose.tools import assert_equal, assert_in, assert_true

@step(u'Then an AddThis widget should appear')
def see_addthis_widget(step):
    assert_equal(len(world.browser.find_by_css('.addthis_toolbox')), 1)

@step(u'Then the AddThis widget should be the 32x32 style')
def see_32x32_style_addthis_widget(step):
    widget = world.browser.find_by_css('.addthis_toolbox').first
    assert_in('addthis_32x32_style', widget['class'])

@step(u'Then a Twitter button should be in the AddThis widget')
def see_twitter_button_in_addthis_widget(step):
    assert_equal(len(world.browser.find_by_css('.addthis_button_twitter')),
                                               1)

@step(u'Then a Facebook button should be in the AddThis widget')
def see_facebook_button_in_addthis_widget(step):
    assert_equal(len(world.browser.find_by_css('.addthis_button_facebook')),
                                               1)

@step(u'Then a email button should be in the AddThis widget')
def see_email_button_in_addthis_widget(step):
    assert_equal(len(world.browser.find_by_css('.addthis_button_email')),
                                               1)

@step(u'Then the generic button should be in the AddThis widget')
def see_compact_button_addthis_widget(step):
    assert_true(len(world.browser.find_by_css('.addthis_button_compact')) >
                0)

@step(u'Then the counter should be in the AddThis widget')
def see_counter_in_addthis_widget(step):
    assert_equal(len(world.browser.find_by_css('.addthis_counter')),
                                               1)
