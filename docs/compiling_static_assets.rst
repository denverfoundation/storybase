=======================
Compiling static assets
=======================

In general static assets are combined, versioned and compressed using
`django-compressor <http://django-compressor.readthedocs.org/en/latest/>`_.

When deploying code, or making changes you may need to run::

    python manage.py collectstatic
    python manage.py compress

However, there are a few cases where precompilation or a additional
compression is needed.  In these cases, there is a Makefile that can be used
to facilitate performing the precompilation or compression.

LESS
====

Styles are written using the `LESS <http://www.lesscss.org/>`_ dynamic
stylesheet language and compiled into a monolithic CSS file, ``style.css``. 

To create the stylesheet, run::

    make styles

in the root project directory.

JavaScript
==========

In cases where JavaScript is not added to a page through a Django template, we
can't use ``django-compressor`` to perform the compression. This is the case
for the embed widget JavaScript as well as some jQuery plugins that are loaded
with ``Modernizr.load()``. In this case, we need to explicitly compress these
scripts by running::

        make scripts

in the root project directory.

A brighter future
=================

Having different means of compression and compilation isn't great, nor is
having to remember to check in the compressed or compiled versions of the
assets into the repository.  A better way to do this might be to implement a
custom storage class for the
`staticfiles app <https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/>`_
that automatically performs the compression/compilation when one runs
``manage.py collectstatic``. 
