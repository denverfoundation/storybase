=========
Upgrading
=========

develop
=======

Django 1.5.* and Django CMS 2.4.* are now the recommended versions. 
Upgrade these packages::

    pip install django>=1.5,<1.6
    pip install django-cms>=2.4,<2.5

In advance of Django removing the ``django.contrib.localflavor``
package from Django core, install the ``django-localflavor`` package::

    pip install django-localflavor

You'll need to run the `upgrade steps for Django CMS 2.4 <http://docs.django-cms.org/en/2.4.0/upgrade/2.4.html>`_.
Please read the upgrading instructions carefully::

    manage.py migrate
    manage.py cms list plugins
    # If any the previous command shows any orphaned plugins run
    # manage.py cms delete_orphaned_plugins
    manage.py cms moderator on

0.16.5 to 0.16.6
================

The builder JavaScript was updated, so you'll have to re-collect the static
assets::

    python manage.py collectstatic

If you're using django-compressor with offline compression, you'll also need
to recompress the JavaScript assets.

    python manage.py compress

Finally, the response of a cached endpoint has changed, so you'll need to clear
the cache, or follow one of the recipes in http://stackoverflow.com/questions/2268417/expire-a-view-cache-in-django
to expire just the cached view.

0.15.* to 0.16
==============

Slugs were added to the Place model.  You'll need to run a schema update::

    python manage.py migrate storybase_geo

The ``activity_guides.html`` CMS template has been deprecated.  Since the
JavaScript for the activity interactions has been incorporated into the
plugin template, you can use any page template.

0.13.* to 0.15
==============

Version 0.15 adds an ``Activity`` model.  A schema migration is needed
to add the database tables for this model::

    python manage.py migrate cmsplugin_storybase

0.12.* to 0.13 
==============

With 0.13, django-registration 1.0 is required.  You'll need to install
the updated version of the package::

    pip install django-registration==1.0

0.11.* to 0.12.0
================

With 0.12.0, the notification types have changed so the user profile model
has to be updated with::

    python manage.py migrate storybase_user

There are also new models for the story reminder notifications whose
database tables need to be initialized::

    python manage.py syncdb

Finally, in order schedule the regular sending of notification emails
you'll need to set up a cron job to call the management command. The easiest
way to set up the cron job is to copy and edit the script in
``scripts/send_story_notifications`` and create a crontab entry like this::

    */2  *    * * *   root    /PATH_TO_SCRIPTS/send_story_notifications 

This version also adds some changes to the ``Help`` model and we need to
use South to update the schema.  Since the ``storybase_help`` app wasn't
previously managed with South, you'll need to convert your installations
to use South for this app::

    ./manage.py migrate storybase_help 0001 --fake

Then you'll need to apply the schema migration::

    ./manage.py migrate storybase_help

There's also a new Django CMS Plugin, so you'll need to run a schema
migration for that as well::

    ./manage.py migrate cmsplugin_storybase

If you create any searchable help, you'll need to update the
search index::

    ./manage.py rebuild_index

We also updated the code base to use the current stable version of Haystack.
We had referenced the GitHub URL for Haystack in the REQUIREMENTS file, so
it's best to uninstall and reinstall Haystack::

    pip uninstall django-haystack
    pip install django-haystack

0.9.* to 0.10.0
===============

With version 0.10.0, the new Tastypie Authorization API is used, requiring
an upgrade to at least version 0.9.15 of Tastypie.  You'll need to 
upgrade Tastypie.  Assuming you're using pip, this looks like::

    pip install --upgrade django-tastypie

0.7 to 0.8
==========

With version 0.8, we started compressing and versioning our JavaScript and
CSS assets using Django Compressor.  You'll need to install this Django app
in your environment::

    pip install django-compressor

It also has some `dependencies <http://django_compressor.readthedocs.org/en/latest/quickstart/#dependencies>`_ which vary depending on how you
configure the app.  Namely, I needed to install BeautifulSoup to use the
``compressor.parser.LxmlParser`` parser::

    pip install "BeautifulSoup<4.0"

If you don't want to use Django Compressor, removing ``compress`` from the
``{% load %}`` statement and the ``{% compress %}`` block tags from these
templates will allow you to continue without Django Compressor: 

* storybase_story/explore_stories.html
* storybase_story/story_builder.html
* storybase_story/story_detail.html
* storybase_story/story_viewer.html
* base.html

You'll also need to remove ``compressor`` from the ``INSTALLED_APPS`` 
setting in your Django settings module.

0.5 to 0.6
==========

With version 0.6, a new Teaser model has been added to the Django CMS
integration.  In order to create the model schema in the database, run::

    manage.py migrate cmsplugin_storybase

0.4 to 0.5
==========

With version 0.5, the primary version of Django that we are supporting will
be Django 1.4.* and the primary version of Django CMS will be 2.3.*.

While we will try to maintain comaptibility with Django 1.3.1 and Django
CMS 2.2, we recommend that you should upgrade your versions of Django and
Django CMS.  

Version 0.5 also updates the dependency of django-notification to version
1.0 and this package should also be upgraded.

To ugprade the dependencies, use the following commands::

    pip install Django==1.4.3
    pip install django-mptt==0.5.2
    pip install django-reversion==1.6
    pip install django-sekizai==0.6.1
    pip install django-cms==2.3.5
    manage.py migrate cms
    pip install django-notification==1.0
