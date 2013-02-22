=========
Upgrading
=========

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
