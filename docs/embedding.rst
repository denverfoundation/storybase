=================
Embedding content
=================

Storybase provides widgets that can be used to embed your story content on
another site.

.. contents::
    :depth: 1
    :local:

Overview
========

The embed codes for the widgets consist of a small snippet of
specially-formatted HTML linking to your content and the inclusion of the
the widget JavaScript file. 

You can generate a widget that displays a single story, or
one that lists stories from a particular organization, project, topic,
tag (keyword) or place. You can also generate a widget that shows a
primary story and also a list of stories.

.. _content-urls:

Content URLs
============

Embed widgets are generated using links to content. This allows users to
get to your content even if JavaScript is disabled or unsupported by
their browser.  The examples below refer to the *slug* portion of the URL
for different types of content.  The term *slug* refers to the shortened,
lowercase and punctuation-replaced version of the item's title or name
that appears in the URL for that item. This table shows the slugs for a few
example URLs:

+-------------------------------------------------------------------------------------------+----------------------------------------------------+
| URL                                                                                       | Slug                                               |
+===========================================================================================+====================================================+
| http://floodlightproject.org/stories/so-much-more-than-butterflies/                       | so-much-more-than-butterflies                      |
+-------------------------------------------------------------------------------------------+----------------------------------------------------+
| http://floodlightproject.org/organizations/the-piton-foundation/                          | the-piton-foundation                               |
+-------------------------------------------------------------------------------------------+----------------------------------------------------+
| http://floodlightproject.org/projects/finding-a-bite-food-access-in-the-childrens-corrid/ | finding-a-bite-food-access-in-the-childrens-corrid |
+-------------------------------------------------------------------------------------------+----------------------------------------------------+

.. _widget-javascript:

Widget JavaScript
=================

The widget JavaScript file can be included in your page like this:

.. code-block:: html

    <script src="http://floodlightproject.org/static/js/widgets.min.js" type="text/javascript"></script>

Including multiple widgets
--------------------------

You can include multiple widgets on a single page. If you do this, you only
need to include the widget JavaScript file once.

Single story
============

To display the widget for a single story:

* Link to the story page for the story you want to embed. Story URLs look like::

    http://floodlightproject.org/stories/SLUG/

* Give the link a class of ``storybase-story-embed``
* Include the :ref:`widget-javascript`

Example
-------

This HTML will display a widget for the story "So much more than butterflies"

.. code-block:: html

    <a href="http://floodlightproject.org/stories/so-much-more-than-butterflies/" class="storybase-story-embed">So much more than butterflies</a>
    <script src="http://floodlightproject.org/static/js/widgets.min.js" type="text/javascript"></script>

Organization stories
====================

To display the widget for a list of an organization's stories:

* Link to the page for the organization you want to embed. Organization URLs look like::

    http://floodlightproject.org/organizations/SLUG/

* Give the link a class of ``storybase-list-embed``
* Include the :ref:`widget-javascript`

Example
-------

This HTML will display a widget for the organization "The Piton Foundation".

.. code-block:: html

    <a href="http://floodlightproject.org/en/organizations/the-piton-foundation/" class=storybase-story-embed">The Piton Foundation</a>
    <script src="http://floodlightproject.org/static/js/widgets.min.js" type="text/javascript"></script>

Project stories
===============

To display the widget for a list of a project's stories:

* Link to the page for the project you want to embed. Project URLs look like::

    http://floodlightproject.org/projects/SLUG/

* Give the link a class of ``storybase-list-embed``
* Include the :ref:`widget-javascript`

Example
-------

This HTML will display a widget for the project "Finding a Bite: Food Access in the Children's Corridor"

.. code-block:: html

    <a href="http://floodlightproject.org/en/projects/finding-a-bite-food-access-in-the-childrens-corrid/" class="storybase-list-embed">Finding a Bite: Food Access in the Children's Corridor</a>
    <script src="http://floodlightproject.org/static/js/widgets.min.js" type="text/javascript"></script>

Topic stories
=============

To display the widget for a list of stories with a given topic:

* Link to the page for the topic you want to embed. Topic URLs look like::

    http://floodlightproject.org/topics/SLUG/

* Give the link a class of ``storybase-list-embed``
* Include the :ref:`widget-javascript`

Example
-------

This HTML will display a widget for the topic "Environment"

.. code-block:: html

    <a href="http://floodlightproject.org/topics/environment/" class="storybase-list-embed">Environment</a>
    <script src="http://floodlightproject.org/static/js/widgets.min.js" type="text/javascript"></script>

Tag (keyword) stories
=====================

To display the widget for a list of stories with a given tag (keyword):

* Link to the page for the tag you want to embed. Tag URLs look like::

    http://floodlightproject.org/tags/SLUG/

* Give the link a class of ``storybase-list-embed``
* Include the :ref:`widget-javascript`

Example
-------

This HTML will display a widget for the tag "storytelling"

.. code-block:: html

    <a href="http://floodlightproject.org/tags/storytelling/" class="storybase-list-embed">Storytelling</a>
    <script src="http://floodlightproject.org/static/js/widgets.min.js" type="text/javascript"></script>

Place stories
=============

To display the widget for a list of stories with a given place:

* Link to the page for the place you want to embed. Place URLs look like::

    http://floodlightproject.org/places/SLUG/

* Give the link a class of ``storybase-list-embed``
* Include the :ref:`widget-javascript`

Example
-------

This HTML will display a widget for the place "Denver"

.. code-block:: html

    <a href="http://floodlightproject.org/places/denver/" class="storybase-list-embed">Denver</a>
    <script src="http://floodlightproject.org/static/js/widgets.min.js" type="text/javascript"></script>

Story and list
==============

To display the widget for a story along with a list of stories:

* Create a ``div`` element with the class ``storybase-story-list-embed``
* Inside the ``div`` element, create a link to the story. Give that link the
  class ``storybase-story``
* Inside the ``div`` element, create a link to the organization, project,
  topic, tag (keyword) or place. Give that link the class ``storybase-list``
* Include the :ref:`widget-javascript`

Example
-------

This HTML will display a widget for the story "Local Grown: Images of the Mo Betta Market"
and stories in the project "Finding a Bite: Food Access in the Children's Corridor":

.. code-block:: html

        <div class="storybase-story-list-embed">
            <a class="storybase-story" href="http://floodlightproject.org/stories/25th-and-welton-images-of-the-mo-betta-market/">Local Grown: Images of the Mo Betta Market</a>
            <a class="storybase-list" href="http://floodlightproject.org/projects/finding-a-bite-food-access-in-the-childrens-corrid/">Finding a Bite: Food Access in the Children's Corridor</a>
        </div>


Widget options
==============

All widget markup accept these options.  They are passed using ``data-``
attributes on the content link elements.

height
------

It's difficult to dynamically size the widget height given
that stories have widely different summary lengths. If the widget appears
too short or too long, you can adjust it using the by specify an explicit
height in pixels. 

**Attribute:** ``data-height``

**Value:** Height in pixels, including the "px" unit, e.g. ``500px``.

Example
~~~~~~~

This HTML will display a widget that has a width of 500 pixels.

.. code-block:: html

    <a href="http://floodlightproject.org/stories/so-much-more-than-butterflies/" class="storybase-story-embed" data-width="500px">So much more than butterflies</a>
    <script src="http://dev.floodlightproject.org/static/js/widgets.min.js" type="text/javascript"></script>

width
-----

**Attribute:** ``data-height``

**Value:** Width in pixels, including the "px" unit, e.g. ``500px``.

Example
~~~~~~~

This HTML will display a widget that has a width of 500 pixels.

.. code-block:: html

    <a href="http://floodlightproject.org/stories/so-much-more-than-butterflies/" class="storybase-story-embed" data-height="500px">So much more than butterflies</a>
    <script src="http://dev.floodlightproject.org/static/js/widgets.min.js" type="text/javascript"></script>
