Floodlight
==========

What is Floodlight?
-------------------

This is the code base behind Floodlight, a powerful story-building website that enables community change makers to inspire action and advance their issues through more substantive, engaging and persuasive data-driven storytelling.

For more information, see http://www.floodlightproject.org/

Changelog
---------

0.6
~~~

* Make titles in Explore view left-justified (#576)
* High-level query API for stories

0.5.5
~~~~~

* Properly register backport i18n tag library.

0.5.4
~~~~~

* Hide error popup for uncaught JavaScript exceptions (#634)

0.5.3
~~~~~

* Log uncaught JavaScript exceptions to the server (#623)

0.5.2
~~~~~

* Wait until viewer images are loaded before resizing containers and captions
  (#622)

0.5.1
~~~~~

* Show error message on uncaught JavaScript exceptions (#623)

0.5
~~~

* Add support for Django 1.4.* and Django CMS 2.3.* (see docs/upgrading.rst)
* Improved asset type selection user interface (#381)
* Simplified flow in the publish/share step of the story builder (#515, #590)
* Use the site-wide sharing widget in the publish/share step of the
  builder (#515)
* Set default featured image in the builder (#515)
* Improved user interface for featured image selection in the builder (#515)
* Story viewer is navigated one page at a time. (#518)
* Builder story summary editor has a character counter and warning when 
  character limit is hit (#530)
* Update and save the story slug when it's initially published (#596)
* Cleanly handle errors and cache response from upstream Creative Commons
  license API (#605)
* "View" button in publish/share step goes to the story viewer and not the
  detail page (#612)
* Update Backbone to version 0.9.10 and Underscore to version 1.4.3
* Update dependency version of django-notification to 1.0 (see 
  docs/upgrading.rst)

0.4.4
~~~~~

* Fixed clobbering of connected story relations when editing a seed story (#611)  

0.4.3
~~~~~

* Added link to connected stories in "Latest Stories" list on homepage (#609)

0.4.2
~~~~~

* Fix preview connected stories (#601)
* Fix display of connected story byline (#607)
* Hide connected stories in latest story list and make their detail
  and viewer views inaccessible (#609)

0.4.1
~~~~~

* Fix for #599 (Home page featured image scaling)

0.4
~~~

* Fix for #146 (Story section list should advance one thumbnail at a time instead of being a continuous scroll)
* Fix for #245 (Placeholders getting cut off in tag view in builder)
* Fix for #417 (Cannot load a previously saved story in builder when accessing through a hash-based URL)
* Fix for #320 (Tools tips on filters on Explore page obscure the drop-down list)
* Fix for #465 (Clean up builder table of contents scroll arrows)
* Basic in-browser integration tests for builder
* Redesigned template selection view in builder (#383)
* Added a subtle border around images and videos in the story viewer (#520)
* Updated home page layout and ability for users to edit home page news
  items (#433, #567)
* Moved layout selector widget in builder (#442)
* Use CSS to "crop" thumbnail images in various templates

0.3.1
~~~~~

* Embedded story widget height attribute needs a 'px'

0.3
~~~

* Fix for #231 (When adding a link in Story Builder text editor "OK" and "Cancel" buttons need to be more prominent)
* Fix for #271 (builder.css has some JS output as selector)
* More prominent social signup/login buttons (#347)
* More visible Summary and Call To Action sections in story viewer (#369)
* Fix for #415 (Builder tour popup falls off screen in Internet Explorer)
* Polyfill for input placeholders in Internet Explorer (#416)
* Users can make a request to create a new Organization (#458)
* Users can make a request to create a new Project (#463)
* Fix for #486 (Call to action overlaps with sharing information on story detail page)
* Usability improvements for adding story sections in the builder (#506)
* Ability to view the builder tour again (#508)
* Usability improvements for modal story viewer (#519)
* Fix for #546 (Incorrect Open Graph meta tags for Project and Organization detail pages and filtered Explore page)
* Fix for #557 (Build step help is shown for other steps)

0.2
~~~

* #237 - Fix builder last saved date in Internet Explorer
* #435 - Sans-serif body fonts
* #448 - s/Communication Preferences/Notifications and Subscriptions/
* #451 - Use museo for headers in story viewer
* #452 - Normalize font sizes in viewer
* #459 - Embedable widget for stories
* #460 - Change story publication status in "My Stories" view
* #461 - Public profile with story lists for each user
* #464 - Full-text search for stories
* #475 - Consistent share widget that wraps AddThis widgets and embed code
* #485 - Cleaned up table styling in "My Stories" view
* #490/#532 - Remove italics in form inputs 
* #491 - Fix missing save button in builder in Internet Explorer
* #493 - IndexError in admin when adding a Project or Organization
* #498 - s/Sponsoring Organizations/Contributing Organizations/
* #500 - Make "Home" link in footer active
* #546 - Fix OpenGraph tags for projects and organizations

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
* `jQuery <http://jquery.org/>`_ by John Resig
* `jQuery Cookie <https://github.com/carhartl/jquery-cookie/>`_ by Klaus Hartl
* `jQuery Condense Plugin <https://github.com/jsillitoe/jquery-condense-plugin>`_ by Joe Sillitoe
* `jQuery Jeditable <http://www.appelsiini.net/projects/jeditable>`_ by Mika Tuupola
* `jQuery Masonry <http://masonry.desandro.com/>`_ by David DeSandro
* `json2.js <https://github.com/douglascrockford/JSON-js/>`_ by Douglas Crockford
* `Formalize <http://formalize.me/>`_ by Nathan Smith
* `Leaflet <http://leaflet.cloudmade.com/>` by CloudMade, Vladimir Agafonkin 
* `LeafClusterer <https://github.com/ideak/leafclusterer/>`_ by Imre Deak
* `Modernizr <http://modernizr.com/>`_
* `Namespace.js <https://github.com/maximebf/Namespace.js>`_ by Maxime Bouroumeau-Fuseau
* `Normalize.css <http://github.com/necolas/normalize.css>`_ by Nicolas Gallagher and Jonathan Neal
* `Select2 <http://ivaynberg.github.com/select2/>`_ by Igor Vaynberg
* `SimpleModal <http://simplemodal.com>`_ by Eric Martin
* `Tooltipster <http://calebjacob.com/tooltipster/>`_ by Caleb Jacob
* `TinyMCE <http://tinymce.com/>`_ by Moxiecode Systems AB
* `Underscore <http://documentcloud.github.com/underscore/>`_ by Jeremy Ashkenas, DocumentCloud
* `WYSIHTML5 <http://xing.github.com/wysihtml5/>`_ by XING AG
