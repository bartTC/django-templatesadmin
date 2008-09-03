from django import forms
from django.utils.translation import ugettext_lazy
from shutil import copy
from templatesadmin.forms import TemplateForm

class TemplateFormWithBackup(TemplateForm):
    backup = forms.BooleanField(
        label = ugettext_lazy(u'Backup file before saving?'),
        required = False,
    )

class DotBackupFilesHook():
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

    def post_save(cls, request, form, template_path):
        pass

    @classmethod
    def generate_form(cls, *args, **kwargs):
        return TemplateFormWithBackup(*args, **kwargs)

