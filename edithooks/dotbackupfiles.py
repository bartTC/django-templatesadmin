from django import forms
from django.utils.translation import ugettext_lazy as _
from shutil import copy

from . import TemplatesAdminHook

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
            raise TemplatesAdminException(_(u'Backup Template \'%s\' has not been saved! Reason: %s' % (template_path, e)))

        return "Backup \'%s.backup\' has been saved." % template_path

    @classmethod
    def contribute_to_form(cls, form):
        form.base_fields['backup'] = forms.BooleanField(
            label = _('Backup file before saving?'),
            required = False,
        )
        return form
