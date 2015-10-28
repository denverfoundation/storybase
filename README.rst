Floodlight
==========

What is Floodlight?
-------------------

This is the code base behind Floodlight, a powerful story-building website that enables community change makers to inspire action and advance their issues through more substantive, engaging and persuasive data-driven storytelling.

For more information, see http://www.floodlightproject.org/


Development Setup
-----------------

Setting up the website can be broken into five parts:

* Install Server Dependencies
* Codebase - Django developement server
* Database - PostgreSQL with PostGIS
* Search Platform - Solr with GIS modification
* Put it all together - migrate and run


Dependencies
~~~~~~~~~~~~

GDAL and GEOS are required for GeoDjango::

    $ sudo apt-get install gdal-bin libgeos-dev

PostGIS is required for the spatial database requirements::

    $ sudo apt-get install postgis


Codebase
~~~~~~~~

Start by cloning the project::

    $ git clone https://github.com/denverfoundation/storybase.git
    $ cd storybase

Copy settings from ``settings/local.sample.py`` to ``settings/local.py``::

    $ cp settings/local.sample.py settings/local.py

Copy environment variables from ``.env.sample`` to ``.env``::

    $ cp .env.sample .env

Inside ``.env``, set ``DJANGO_SETTINGS_MODULE`` to ``settings.local``.

In a `virtual environment <https://virtualenv.pypa.io/en/latest/>`_, install the dependencies with pip::

    $ pip install -r requirements.txt


Database
~~~~~~~~

The database name, user, and password must be set via `Django Database URL <http://crate.io/packages/dj-database-url/>`_
as an environment variable inside ``.env``.

After creating a database, you will need to add the postgis extension::

    CREATE EXTENSION postgis;


Search Platform
~~~~~~~~~~~~~~~

Clone the modified Solr::

    $ git clone https://github.com/denverfoundation/storybase_solr.git


Putting it all together
~~~~~~~~~~~~~~~~~~~~~~~

Start by spinning up the Solr system::

    $ cd storybase_solr
    $ java -Dsolr.solr.home=multicore -jar start.jar

Migrate the database from the codebase directory::

    $ python manage.py migrate

Finally, run the app::

    $ python manage.py runserver


Rebuild/Refresh Solr Indexes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To rebuild the indexes (destructive), run::

    $ python manage.py rebuild_index

To refresh the indexes, run::

    $ python manage.py update_index


License
~~~~~~~

This software is licensed under the `MIT License <http://opensource.org/licenses/MIT>`_

Authors
~~~~~~~

* Geoff Hing - https://github.com/ghing/
* Eric Miller - https://github.com/patternleaf/

On the shoulders of giants
--------------------------

This project includes a number of excellent open-source libraries:

* `The 1140px Grid V2 <http://cssgrid.net/>`_ by Andy Taylor
* `Backbone <http://documentcloud.github.com/backbone/>`_ by Jeremy Ashkenas, DocumentCloud
* `D3 <http://mbostock.github.com/d3/>`_ by Michael Bostock
* `Font Awesome <http://fortawesome.github.com/Font-Awesome/>`_ by Dave Gandy
* `Guiders.js <https://github.com/jeff-optimizely/Guiders-JS>`_ by Optimizely
* `Handlebars <http://handlebarsjs.com/>`_ by Yehuda Katz
* `HTML5 Boilerplate <http://html5boilerplate.com/>`_
* `imagesLoaded <https://github.com/desandro/imagesloaded>`_ by David DeSandro
* `JavaScript Pretty Date <http://ejohn.org/blog/javascript-pretty-date/>`_ by John Resig
* `jQuery <http://jquery.org/>`_ by John Resig
* `jQuery Cookie <https://github.com/carhartl/jquery-cookie/>`_ by Klaus Hartl
* `jQuery Condense Plugin <https://github.com/jsillitoe/jquery-condense-plugin>`_ by Joe Sillitoe
* `jQuery Iframe Transport <http://cmlenz.github.com/jquery-iframe-transport/>`_ by Christopher Lenz
* `jQuery Masonry <http://masonry.desandro.com/>`_ by David DeSandro
* `json2.js <https://github.com/douglascrockford/JSON-js/>`_ by Douglas Crockford
* `Formalize <http://formalize.me/>`_ by Nathan Smith
* `Leaflet <http://leaflet.cloudmade.com/>` by CloudMade, Vladimir Agafonkin
* `LeafClusterer <https://github.com/ideak/leafclusterer/>`_ by Imre Deak
* `Modernizr <http://modernizr.com/>`_
* `Normalize.css <http://github.com/necolas/normalize.css>`_ by Nicolas Gallagher and Jonathan Neal
* `Respond.js <https://github.com/scottjehl/Respond>`_ by Scott Jehl
* `Select2 <http://ivaynberg.github.com/select2/>`_ by Igor Vaynberg
* `Tooltipster <http://calebjacob.com/tooltipster/>`_ by Caleb Jacob
* `TinyMCE <http://tinymce.com/>`_ by Moxiecode Systems AB
* `Underscore <http://documentcloud.github.com/underscore/>`_ by Jeremy Ashkenas, DocumentCloud
* `WYSIHTML5 <http://xing.github.com/wysihtml5/>`_ by XING AG
