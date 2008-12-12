===============
Templates Admin
===============

Templates Admin is a tiny, nifty application for your Django_ project to edit
your templates, that are stored on your disk, via an admin interface.

Originally this app was inspired by dbtemplates_.

.. _Django: http://www.djangoproject.com/
.. _dbtemplates: http://code.google.com/p/django-dbtemplates/

Installation:
=============

1. Put ``templatesadmin`` into your INSTALLED_APPS setting.

2. Add this line to your urlconf::
    
    (r'^templatesadmin/',include('templatesadmin.urls')),

3. Create a group ``TemplateAdmins`` and put all users in there, who should been
   able to edit templates. You don't need to grant any permissions to that group.
   Just call it ``TemplateAdmins``.
   
   Keep in mind that also Superusers (*is_admin* flag) must belong to this group, if
   they should been able to edit templates. The group name is case-sensitive!
   
4. Point your webbrowser to ``http://localhost/templatesadmin/`` and start 
   editing.
   
Optional Settings:
==================

There are some settings that you can override in your ``settings.py``:

1. ``TEMPLATESADMIN_GROUP``: The name of your group of your TemplatesAdmin
   Users. 
   
   Default: ``TemplateAdmins``
   
2. ``TEMPLATESADMIN_VALID_FILE_EXTENSIONS``: A tuple of file-extensions (without
   the leading dot) that are editable by TemplatesAdmin.
   
   Default::
   
    TEMPLATESADMIN_VALID_FILE_EXTENSIONS = (
        'html', 
        'htm', 
        'txt', 
        'css', 
        'backup'
    )

3. ``TEMPLATESADMIN_TEMPLATE_DIRS``: A tuple of directories you want your users
   to edit, instead of all templates.

   Default: All user-defined and application template-dirs.

4. ``TEMPLATESADMIN_HIDE_READONLY``: A boolean to wether enable or disable
   displaying of read-only templates.
   
   Default: ``False``

5. ``TEMPLATESADMIN_EDITHOOKS``: A tuple of callables edithooks. Edithooks are
   a way to interact with changes made on a template. Think of a plugin system.

   There are two builtin edithooks:
   
   - ``dotbackupfiles.DotBackupFilesHook``: Creates a copy of the original file
     before overwriting, naming it ``<oldname>.backup``.
   - ``gitcommit.GitCommitHook``: Commits your templates after saving via git
     version control.

   You can define your own edithooks, see above hooks as example. 
   
   Default::
   
    TEMPLATESADMIN_EDITHOOKS = (    
        'templatesadmin.edithooks.dotbackupfiles.DotBackupFilesHook',
    )
   
Dependencies:
=============

There are no external dependencies required for this app. Even if it looks like
django-admin, it just needs it Stylesheets. So make sure you have set the
``settings.ADMIN_MEDIA_PREFIX`` url.

You have to enable ``django.contrib.auth`` and ``django.contrib.sessions`` in your
``INSTALLED_APPS`` settings.

LICENSE:
========

This application is licensed under the ``Beerware License``.
See ``LICENSE`` for details.

Changelog:
==========

**v0.5.2 (2008-12-12)**

* Added a edithook for dealing with mercurial repositories. Thank you v.oostveen! (Issue3_)
* Fixed handling of newline characters at the end of the file, which causes to 
  delete the last character. (Issue4_)

.. _Issue3: http://code.google.com/p/django-templatesadmin/issues/detail?id=3
.. _Issue4: http://code.google.com/p/django-templatesadmin/issues/detail?id=4
 
  
  