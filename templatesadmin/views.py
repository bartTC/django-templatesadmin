import os
import codecs
from datetime import datetime
from stat import ST_MTIME, ST_CTIME
from re import search

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loaders.app_directories import app_template_dirs
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache

from templatesadmin.forms import TemplateForm
from templatesadmin import TemplatesAdminException

# Default settings that may be overriden by global settings (settings.py)
TEMPLATESADMIN_VALID_FILE_EXTENSIONS = getattr(
    settings,
    'TEMPLATESADMIN_VALID_FILE_EXTENSIONS',
    ('html', 'htm', 'txt', 'css', 'backup',)
)

TEMPLATESADMIN_GROUP = getattr(
    settings,
    'TEMPLATESADMIN_GROUP',
    'TemplateAdmins'
)

TEMPLATESADMIN_EDITHOOKS = getattr(
    settings,
    'TEMPLATESADMIN_EDITHOOKS',
    ('templatesadmin.edithooks.dotbackupfiles.DotBackupFilesHook', )
)

TEMPLATESADMIN_HIDE_READONLY = getattr(
    settings,
    'TEMPLATESADMIN_HIDE_READONLY',
    False
)

if str == type(TEMPLATESADMIN_EDITHOOKS):
    TEMPLATESADMIN_EDITHOOKS = (TEMPLATESADMIN_EDITHOOKS,)

_hooks = []

for path in TEMPLATESADMIN_EDITHOOKS:
    # inspired by django.template.context.get_standard_processors
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = __import__(module, {}, {}, [attr])
    except ImportError, e:
        raise ImproperlyConfigured('Error importing edithook module %s: "%s"' % (module, e))
    try:
        func = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" callable request processor' % (module, attr))

    _hooks.append(func)

TEMPLATESADMIN_EDITHOOKS = tuple(_hooks)

_fixpath = lambda path: os.path.abspath(os.path.normpath(path))

TEMPLATESADMIN_TEMPLATE_DIRS = getattr(
    settings,
    'TEMPLATESADMIN_TEMPLATE_DIRS', [
        d for d in list(settings.TEMPLATE_DIRS) + \
        list(app_template_dirs) if os.path.isdir(d)
    ]
)

TEMPLATESADMIN_TEMPLATE_DIRS = [_fixpath(dir) for dir in TEMPLATESADMIN_TEMPLATE_DIRS]

def user_in_templatesadmin_group(user):
    try:
        user.groups.get(name=TEMPLATESADMIN_GROUP)
        return True
    except ObjectDoesNotExist:
        return False

@never_cache
@user_passes_test(lambda u: user_in_templatesadmin_group(u))
@login_required
def listing(request,
             template_name='templatesadmin/overview.html',
             available_template_dirs=TEMPLATESADMIN_TEMPLATE_DIRS):

    template_dict = []
    for templatedir in available_template_dirs:
        for root, dirs, files in os.walk(templatedir):
            for f in sorted([f for f in files if f.rsplit('.')[-1] \
                      in TEMPLATESADMIN_VALID_FILE_EXTENSIONS]):
                full_path = os.path.join(root, f)
                l = {
                     'templatedir': templatedir,
                     'rootpath': root,
                     'abspath': full_path,
                     'modified': datetime.fromtimestamp(os.stat(full_path)[ST_MTIME]),
                     'created': datetime.fromtimestamp(os.stat(full_path)[ST_CTIME]),
                     'writeable': os.access(full_path, os.W_OK)
                }

                # Do not fetch non-writeable templates if settings set.
                if (TEMPLATESADMIN_HIDE_READONLY == True and \
                    l['writeable'] == True) or \
                   TEMPLATESADMIN_HIDE_READONLY == False:
                    try:
                        template_dict += (l,)
                    except KeyError:
                        template_dict = (l,)

    template_context = {
        'messages': request.user.get_and_delete_messages(),
        'template_dict': template_dict,
        'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
    }

    return render_to_response(template_name, template_context,
                              RequestContext(request))
@never_cache
def modify(request,
           path,
           template_name='templatesadmin/edit.html',
           base_form=TemplateForm,
           available_template_dirs=TEMPLATESADMIN_TEMPLATE_DIRS):

    template_path = _fixpath(path)

    # Check if file is within template-dirs
    if not any([template_path.startswith(templatedir) for templatedir in available_template_dirs]):
        request.user.message_set.create(message=_('Sorry, that file is not available for editing.'))
        return HttpResponseRedirect(reverse('templatesadmin-overview'))

    if request.method == 'POST':
        formclass = base_form
        for hook in TEMPLATESADMIN_EDITHOOKS:
            formclass.base_fields.update(hook.contribute_to_form(template_path))

        form = formclass(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']

            try:
                for hook in TEMPLATESADMIN_EDITHOOKS:
                    pre_save_notice = hook.pre_save(request, form, template_path)
                    if pre_save_notice:
                        request.user.message_set.create(message=pre_save_notice)
            except TemplatesAdminException, e:
                request.user.message_set.create(message=e.message)
                return HttpResponseRedirect(request.build_absolute_uri())

            # Save the template
            try:
                f = open(template_path, 'r')
                file_content = f.read()
                f.close()

                # browser tend to strip newlines from <textarea/>s before
                # HTTP-POSTing: re-insert them if neccessary

                # content is in dos-style lineending, will be converted in next step
                if (file_content[-1] == '\n' or file_content[:-2] == '\r\n') \
                   and content[:-2] != '\r\n':
                    content = u"%s\r\n" % content

                # Template is saved in unix-style, save in unix style.
                if None == search("\r\n", file_content):
                    content = content.replace("\r\n", "\n")

                f = codecs.open(template_path, 'w', 'utf-8')
                f.write(content)
                f.close()
            except IOError, e:
                request.user.message_set.create(
                    message=_('Template "%(path)s" has not been saved! Reason: %(errormsg)s' % {
                        'path': path,
                        'errormsg': e
                    })
                )
                return HttpResponseRedirect(request.build_absolute_uri())

            try:
                for hook in TEMPLATESADMIN_EDITHOOKS:
                    post_save_notice = hook.post_save(request, form, template_path)
                    if post_save_notice:
                        request.user.message_set.create(message=post_save_notice)
            except TemplatesAdminException, e:
                request.user.message_set.create(message=e.message)
                return HttpResponseRedirect(request.build_absolute_uri())

            request.user.message_set.create(
                message=_('Template "%s" was saved successfully.' % path)
            )
            return HttpResponseRedirect(reverse('templatesadmin-overview'))
    else:
        template_file = codecs.open(template_path, 'r', 'utf-8').read()

        formclass = TemplateForm
        for hook in TEMPLATESADMIN_EDITHOOKS:
            formclass.base_fields.update(hook.contribute_to_form(template_path))

        form = formclass(
            initial={'content': template_file}
        )

    template_context = {
        'messages': request.user.get_and_delete_messages(),
        'form': form,
        'short_path': path,
        'template_path': path,
        'template_writeable': os.access(template_path, os.W_OK),
        'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
    }

    return render_to_response(template_name, template_context,
                              RequestContext(request))

# For backwards compatibility and secure out-of-the-box views
overview = user_passes_test(lambda u: user_in_templatesadmin_group(u))(login_required(listing))
edit = user_passes_test(lambda u: user_in_templatesadmin_group(u))(login_required(modify))
