from django import forms
from django.utils.translation import ugettext_lazy
from templatesadmin import TemplatesAdminException
from templatesadmin.forms import TemplateForm

import subprocess
import os

class ChangeCommentTemplateForm(TemplateForm):
    backup = forms.CharField(
        widget=forms.TextInput(attrs={'size':'100'}),
        label = ugettext_lazy(u'Change message'),
        required = False,
    )

class GitCommitHook():
    '''
    Backup File before saving
    '''

    @classmethod
    def pre_save(cls, request, form, template_path):
        pass

    @classmethod
    def post_save(cls, request, form, template_path):
        dir, file = os.path.dirname(template_path) + "/", os.path.basename(template_path)

        if request.user.first_name and request.user.last_name:
            author = "%s %s" % (request.user.first_name, request.user.last_name)
        else:
            author = request.user.username

        message = '--'

        backup = form.cleaned_data['backup']
        if backup:
            message = form.cleaned_data['backup']

        command = (
            'GIT_COMMITTER_NAME="%(author)s" GIT_COMMITER_EMAIL="%(email)s" '
            'GIT_AUTHOR_NAME="%(author)s" GIT_AUTHOR_EMAIL="%(email)s" '
            'git commit -F - -- %(file)s'
        ) % {
          'file': file,
          'author': author,
          'email': request.user.email,
        }

        # Stolen from gitpython's git/cmd.py
        proc = subprocess.Popen(
            args=command,
            shell=True,
            cwd=dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            proc.stdin.write(message)
            proc.stdin.close()
            stderr_value = proc.stderr.read()
            stdout_value = proc.stdout.read()
            status = proc.wait()
        finally:
	    proc.stderr.close()

        if status != 0:
            print status
            raise TemplatesAdminException("Error while executing %s: %s" % (command, stderr_value.rstrip(), ))

        return stdout_value.rstrip()

    @classmethod
    def generate_form(cls, *args, **kwargs):
        return ChangeCommentTemplateForm(*args, **kwargs)
