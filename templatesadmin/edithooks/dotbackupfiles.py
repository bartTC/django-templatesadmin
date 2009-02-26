from shutil import copy

from django import forms
from django.utils.translation import ugettext_lazy as _

from templatesadmin.edithooks import TemplatesAdminHook
from templatesadmin import TemplatesAdminException

class DotBackupFilesHook(TemplatesAdminHook):
    '''
    Backup File before saving
    '''

    @classmethod
    def pre_save(cls, request, form, template_path):
        backup = form.cleaned_data['backup']

        if not backup:
            return None

        try:
            copy(template_path, '%s.backup' % template_path)
        except IOError, e:
            raise TemplatesAdminException(
                _(u'Backup Template "%(path)s" has not been saved! Reason: %(errormsg)s' % {
                    'path': template_path,
                    'errormsg': e
                })
            )

        return "Backup \'%s.backup\' has been saved." % template_path

    @classmethod
    def contribute_to_form(cls, template_path):
        return dict(backup=forms.BooleanField(
            label = _('Backup file before saving?'),
            required = False,
        ))
