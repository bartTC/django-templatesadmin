from django.core.urlresolvers import reverse
import os
from datetime import datetime
from stat import ST_MTIME, ST_CTIME, S_IWRITE
from base64 import urlsafe_b64decode

from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.conf import settings
from django.template.loaders.app_directories import app_template_dirs

from templatesadmin.forms import TemplateForm

TEMPLATEADMIN_VALID_FILE_EXTENSIONS = getattr(
    settings,
    'TEMPLATEADMIN_VALID_FILE_EXTENSIONS', 
    ('html', 'htm', 'txt', 'css', 'backup',)
)

def overview(request, template_name='templatesadmin/overview.html'):
    
    templatedirs = [d for d in settings.TEMPLATE_DIRS + \
                    app_template_dirs if os.path.isdir(d)]
    
    template_dict = []
    for templatedir in templatedirs:
        for root, dirs, files in os.walk(templatedir):
            for f in sorted([f for f in files if f.rsplit('.')[-1] \
                      in TEMPLATEADMIN_VALID_FILE_EXTENSIONS]):
                full_path = os.path.join(root, f)
                l = {
                     'rootpath': root,
                     'abspath': full_path,
                     'modified': datetime.fromtimestamp(os.stat(full_path)[ST_MTIME]),
                     'created': datetime.fromtimestamp(os.stat(full_path)[ST_CTIME]),
                     'writeable': os.access(full_path, os.W_OK)
                }                
                try:
                    template_dict += (l,)
                except KeyError:
                    template_dict = (l,)

    template_context = {
        'messages': request.user.get_and_delete_messages(),
        'template_dict': template_dict,
        'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
    }        

    return render_to_response(template_name, template_context)
    
def edit(request, path, template_name='templatesadmin/edit.html'):

    template_path = urlsafe_b64decode(str(path))
    template_file = open(template_path).read()    
    short_path = template_path.rsplit('/')[-1]
    
    templatedirs = [d for d in settings.TEMPLATE_DIRS + \
                    app_template_dirs if os.path.isdir(d)]
    
    # TODO: Check if file is within template-dirs and writeable
    if request.method == 'POST':
        form = TemplateForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            backup = form.cleaned_data['backup']
            
            # Backup File before saving
            if backup:
                try:
                    f = open('%s.backup' % template_path, 'w')
                    f.write(template_file)
                    f.close()
                except IOError, e:
                    request.user.message_set.create(
                        message=_(u'Backup Template \'%s\' has not been saved! Reason: %s' % (short_path, e))
                    )
                    return HttpResponseRedirect(request.build_absolute_uri())
            
            # Save the template
            try:
                f = open(template_path, 'w')
                f.write(content)
                f.close()
            except IOError, e:
                request.user.message_set.create(
                    message=_(u'Template \'%s\' has not been saved! Reason: %s' % (short_path, e))
                )
                return HttpResponseRedirect(request.build_absolute_uri())
            
            request.user.message_set.create(
                message=_(u'Template \'%s\' was saved successfully' % short_path)
            )
            return HttpResponseRedirect(reverse('templatesadmin-overview'))
    else:
        form = TemplateForm(
            initial={'content': template_file}
        )
    
    template_context = {
        'messages': request.user.get_and_delete_messages(),
        'form': form,
        'short_path': short_path,
        'template_path': template_path,
        'template_writeable': os.access(template_path, os.W_OK),
        'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
    }        

    return render_to_response(template_name, template_context)
