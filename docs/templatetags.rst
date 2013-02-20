=============
Template Tags
=============

StoryBase template tags are arranged in a number of different tag libraries
which must be loaded using Django's ``load`` tag.

Example::

    {% load story %}


storybase_menu
--------------

Template tags used for rendering ``storybase.menu.Menu`` instances.

storybase_menu
^^^^^^^^^^^^^^

Example:

    {% load storybase_menu %}
    {% storybase_menu "my_account" "storybase_user/account_menu.html" request.path %}

The ``storybase_menu`` tag takes three arguments.  The first is a string
matching the ID used when instantiating the ``storybase.menu.Menu`` '
instance. The second is the name of the template to be used to render the
menu.  The third optional argument is the path of the current view, used
to identify the active item in the menu.  ``request.path`` works well for
this third argument, asuming ``django.core.context_processors.request``
is included in ``settings.TEMPLATE_CONTEXT_PROCESSORS``.

The template context includes a ``menu`` variable which is the 
``Menu`` instance and ``menu_items``, a list of the menu items from the 
menu.
    
story
-----

Template tags related to displaying stories.

banner
^^^^^^

Display a tiled map of story images as seen on the Floodlight homepage.

It can take a positional argument corresponding to the ``banner_id`` of a 
``Banner`` subclass to use a particular method of selecting stories in the 
banner.

Example::

    {% banner "random" %}

This example uses the ``RandomBanner`` implementation, which selects a
random set of stories for the banner.

The ``banner`` tag can also take keyword arguments that are passed to the
constructor of the banner implementation.

Example::

    {% banner "topic" slug="arts-and-culture" %}

This use of the ``banner`` tag uses the ``TopicBanner`` implementation which
selects stories associated with a topic with the specified ``slug``.

If the ``banner`` tag is used with no arguments, an implementation will be
selected at random from the registered ``Banner`` subclasses, to select
stories shown in the banner.

Example::

    {% banner %}

If ``settings.GA_PROPERTY_ID`` is set, links to stories in the banner will
have URL parameters for `Google Analytics Custom Campaigns <http://support.google.com/analytics/bin/answer.py?hl=en&answer=1033863>`_ 
added to the URL to help track which banner strategies are most effective
for connecting site visitors to stories.
