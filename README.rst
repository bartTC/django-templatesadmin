===============
Templates Admin
===============

Templates Admin is a tiny, nifty application for your Django_ project to edit your templates on the
fly, on your production server.

Originally this app was inspired by the (more) powerful dbtemplates_.

.. _Django: http://www.djangoproject.com/
.. _dbtemplates: http://code.google.com/p/django-dbtemplates/

Installation:
=============

1. Put ``templatesadmin`` into your INSTALLED_APPS setting.
2. Add this line to your urlconf::
    
    (r'^templatesadmin/',include('templatesadmin.urls')),

3. Make this application *readonly* by Administrators. (Description follows)

LICENSE:
========

This application is licensed under the ``New BSD License``.
