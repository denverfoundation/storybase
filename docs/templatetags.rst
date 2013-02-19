=============
Template Tags
=============

StoryBase template tags are arranged in a number of different tag libraries
which must be loaded using Django's ``load`` tag.

Example::

    {% load story %}

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
