Floodlight
==========

What is Floodlight?
-------------------

This is the code base behind Floodlight, a powerful story-building website that enables community change makers to inspire action and advance their issues through more substantive, engaging and persuasive data-driven storytelling.

For more information, see http://www.floodlightproject.org/

Changelog
---------

0.19.3
~~~~~~

* Handle SSLErrors from oEmbed request gracefully.  Cache oEmbed responses (#946)

0.19.2
~~~~~~

* Fix viewer sticky header on Android (#942)

0.19.1
~~~~~~

* Validation and error response for too-long dataset URLS (#940)

0.19.0
~~~~~~

* Responsive design in templates and styles (#774)

0.18.0
~~~~~~

* Fix Leaflet popup styles on explore page (#367)
* Remove "Story Information" workflow step and move editing of story title and
  byline into the header (#578)
* Simplified story building workflow steps (#579)
* Refinement of section reordering behaviors (#903, #905)
* Fix issue with automatic setting of featured image (#908)
* Simple validation of story elements on publish (#909)
* Reassign assets to new containers on layout changes (#914)
* Refactor explorer stylesheets
* Make builter tools menu a drop-down
* More compact header
* Refactor Backbone code for handling section to asset relationships

0.17.4
~~~~~~

* Allow "<br>" tags in story summary and call to action prompt fields (#912)

0.17.3
~~~~~~

* Fix typo introduced in fix for #894

0.17.2
~~~~~~

* Sanitize HTML in story summary and call to action (#894)

0.17.1
~~~~~~

* Add icon for "Successes and Obstacles" template (#895)

0.17.0
~~~~~~

* Support Django 1.5/Django CMS 2.4 (#660)
* Captions pop up at top of asset on mouseover in viewer (#717)
* Auto-expanding text editor (#844)
* Autosave for text assets (#847, #848)
* Scroll to top of next section when switching sections in viewer (#852)
* Don't send site contact message notification from user email address (#886)

0.16.7
~~~~~~

* Take care when using JavaScript reserved word "class" (#884)

0.16.6
~~~~~~

* Convert data fron Creative Commons license endpoint to JSON (#878)

0.16.5
~~~~~~

* Support oEmbed for short Soundcloud URLs (#877)

0.16.4
~~~~~~

* Fix typo in embed widget documentation

0.16.3
~~~~~~

* Add "My Stories" link to builder tools menu (#784)
* Builder alerts fade out in 8 seconds instead of 15 (#870)

0.16.2
~~~~~~

* Make activity guides styling and interaction available on any page (#874)
* Deprecate activity guides template (``activity_guides.html``) (#874)

0.16.1
~~~~~~

* Remove default data-height attribute from embed code shown in embed button
  popup.

0.16
~~~~

* Add slug field to Place model
* Updated embed widget (#741)
* Upgrade Font Awesome to version 3.2.1 (#868)

0.15.1
~~~~~~

* Custom template, updated styling and interactions for activity guide (#864)
* Upgrade less.js (used in development) to version 1.4.1
* MIT license

0.15
~~~~

* Activity content type (#853)
* Updated Fabric tasks for deployment and installation
* Updated Fabric tasks to install Solr from tarball instead of updating the
  old Ubuntu packages

0.14
~~~~

* RSS feed for stories (#816)
* Fix links for connected stories in builder and notification emails (#856)
* Add slugs as id attribute for help item headers (#861) 

0.13.3
~~~~~~

* Support both instagram.com and instagr.am URLs for oEmbeding assets (#860)

0.13.2
~~~~~~

* Update default summary text in the builder, encouraging summaries < 250
  characters (#858)
* Fix CSV export of user information (#859)

0.13.1
~~~~~~

* Fix typo in password reset form template (#849)

0.13
~~~~

* Warning message for long titles (#562)
* Upgrade jQuery tooltipster plugin (#562)
* Support for django-registration 1.0 (#786)
* Clearer account activation behavior (#836)
* Link to builder for empty story list (#840)

0.12.2
~~~~~~

* Only show one asset content (file, URL, body) input at a time (#767)
* Fix dataset file replacement in IE8/IE9 (#829)
* Fix featured image pills in IE8 (#837)

0.12.1
~~~~~~

* Fix rendering of Publish/Share workflow step in IE8/IE9 (#830)

0.12
~~~~

* Searchable help (#507)
* Story notification emails (#580)
* Real-time search index updates that use Haystack 2.0+ APIs (#817)
* Fix formatting of header on intermediary page in social registration
  flow (#826)

0.11.3
~~~~~~

* Gracefully handle parse errors when trying to generate thumbnail from HTML
  asset (#814)

0.11.2
~~~~~~

* Updated asset help (#641)

0.11.1
~~~~~~

* Show embedded Google Charts in builder (#187)
* More prominent confirmation messages (#533)
* Resize sharing widget with textarea (#545)
* Switch to section help from container help when drawer is closed (#641)
* Show suggested summary, section titles and call to action as placeholders 
  (#722)
* Remove in-place editing of captions (#765)
* Header always visible as section scrolls in viewer (#772)
* Fix editing of image-based assets (#794)
* Show suggested section title in section list for untitled sections (#798)
* Render non-oEmbed URL-based chart assets using an img tag (#803)
* Fix scaling of images and containers in viewer (#807)
* Ability to filter stories in admin based on whether or not they're used
  as a template (#808)

0.11
~~~~

* Associate datasets with assets instead of the story (#583, #760)
* Progress bar for asset and dataset file uploads (#732)
* "Get the Data" button on story detail page to make datasets more 
  prominent (#733)
* Show HTML-based assets as icons in asset drawer (#770)
* Properly handle click of chevron in next/previous buttons in viewer (#785)

0.10.6
~~~~~~

* Workaround for page width getting truncated in mobile Safari (#774)

0.10.5
~~~~~~

* Fix broken viewer in IE < 9 due to lack of support for Array.indexOf (#766)

0.10.4
~~~~~~

* Fix behavior and display of assets when dragging from unused asset
  drawer (#746)
* Fix removal of assets after switching workflow steps (#764)

0.10.3
~~~~~~

* Wrap long URLs on organization and project detail pages (#759)

0.10.2
~~~~~~

* Only show character count warning for summary (#673)

0.10.1
~~~~~~

* Fix restriction of asset types in templates (#763)

0.10.0
~~~~~~

* Support latest version of Tastypie (#614)
* Preserve file type when creating thumbnails (#726)
* Support replacing uploaded image assets (#738)
* Don't automatically add linebreaks to story summary (#740)

0.9.7
~~~~~

* Make viewer header not be position:fixed (#684)
* Prevent wrapping in header-right menu (#702)
* Wrap Backbone modules in self-executing anonymous functions (#710)
* Update thumbnail view lookup keys when initial sections are first saved (#725)
* Fix race condition on initial save (#728)
* Invalidate cached places list when story's places are updated (#730)
* Remove dependency on Namespace.js

0.9.6
~~~~~

* Fix race condition when updating Solr index when a section is removed (#723)

0.9.5
~~~~~

* Fix table of contents elements (#715)

0.9.4
~~~~~

* Fix table of contents toggling (#709)

0.9.3
~~~~~

* Add ability to close alerts before they fade out
* Avoid duplicate alert messages
* Move search bar to top of map in explorer (#559)
* Fix scrolling of asset drawer (#692)
* Supress builder tour when user clicks the "X" icon (#697)
* More subtle response when story is saved (#548)

0.9.2
~~~~~

* Wire up links to detail view of news items in homepage slider (#703)

0.9.1
~~~~~

* Use mock geocoder in tests unless user explicitely specifies a geocoder
  in the settings (#700)

0.9
~~~

* Prevent assigning multiple assets to the same section/container (#595)
* Prevent submitting the builder asset creation form when either a file or
  URL has not been specified (#606)
* Add display of connected story featured images in viewer (#610)
* Add weight field to Story model and sort latest stories by this field
  (#625) 
* Sort latest projects and latest organizations lists by published
  timestamp (#625)
* Sort projects in the projects list view by published timestamp (#625)
* Show asset views after switching between workflow steps (#696)

0.8.10
~~~~~~

* Fix positioning of builder workflow step tabs (#695)

0.8.9
~~~~~

* Properly dehydrate related fields when they haven't been cached (#566)

0.8.8
~~~~~

* Properly evaluate logged-in-user when previewing stories (#690)

0.8.7
~~~~~

* Fix regression where section list width was being incorrectly set for
  newly created stories (#556)

0.8.6
~~~~~

* Maintain section list height, even when there are a large number of sections (#556)

0.8.5
~~~~~

* Fix connected story links in viewer in modal IFRAME (#487)

0.8.4
~~~~~

* Don't write to browser history when opening viewer in modal IFRAME (#487)

0.8.3
~~~~~

* Escape JSON when output inside <script> tags (#658)

0.8.2
~~~~~

* Match oEmbed URLs beginning with either "http://" or "https://" (#681)

0.8.1
~~~~~

* Fix duplicate CSS being included in builder

0.8
~~~

* Prevent saving multiple assets to the same section and container (#535)
* Quote styles in viewer (#565)
* Make placeholder behavior in builder form fields more consistent (#616)
* Use django-compressor to compress and version static assets (#624)
* Add space to content in viewer to accomdate bottom bar (#627)
* Fix alignment of builder toolbar icons in Chrome >= 0.25 (#649)
* Do better housekeeping of Backbone views for asset editing (#671)


0.7
~~~

* Wired in home page banner (#198)
* Better cleanup of Select2 instances on Explore page (#480)
* Made link and button colors consistent across the site (#514)
* Move "View all stories" button higher up on project and organization
  detail pages (#531)
* Make "My Account" menu consistent in the sidebar and megamenu (#544)
* Make titles in Explore view left-justified (#576)
* Include count and link to connected stories in homepage featured slider
  and explore pasge (#629)
* Apphook to connect news items feed to a CMS page (#646)
* High-level query API for stories
* Implemented a reusable menu class and template tag for rendering menus
* (Mostly) remove hard-coded URLs from navigation
* Factor navigation menus into separate templates

0.6.5
~~~~~

* Use Django 1.4's signature for ``PasswordResetForm.save`` (#661)

0.6.4
~~~~~

* Allow superusers to open any story in builer (#657)

0.6.3
~~~~~

* Only log JavaScript errors to the server once (#635)

0.6.2
~~~~~

* Workaround for multiple assets per section container issue (#534, #535)

0.6.1
~~~~~

* Fix width of builder section list in Chrome (#648)

0.6
~~~

* Ability to add Teasers to CMS Pages

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
