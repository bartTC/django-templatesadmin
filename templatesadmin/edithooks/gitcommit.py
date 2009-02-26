from django import forms
from django.utils.translation import ugettext_lazy as _
from templatesadmin import TemplatesAdminException
from templatesadmin.edithooks import TemplatesAdminHook

import subprocess
import os

class GitCommitHook(TemplatesAdminHook):
    '''
    Commit to git after saving
    '''

    @classmethod
    def post_save(cls, request, form, template_path):
        dir, file = os.path.dirname(template_path) + "/", os.path.basename(template_path)

        if request.user.first_name and request.user.last_name:
            author = "%s %s" % (request.user.first_name, request.user.last_name)
        else:
            author = request.user.username

        message = form.cleaned_data['commitmessage'] or '--'

        command = (
            'GIT_COMMITTER_NAME="%(author)s" GIT_COMMITER_EMAIL="%(email)s" '
            'GIT_AUTHOR_NAME="%(author)s" GIT_AUTHOR_EMAIL="%(email)s" '
            'git commit -F - -- %(file)s'
        ) % {
          'file': template_path,
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
            proc.stdin.write(message.encode('utf-8'))
            proc.stdin.close()
            stderr_value = proc.stderr.read()
            stdout_value = proc.stdout.read()
            status = proc.wait()
        finally:
            proc.stderr.close()

        if status != 0:
            raise TemplatesAdminException("Error while executing %s: %s" % (command, stderr_value.rstrip(), ))

        return stdout_value.rstrip()

    @classmethod
    def contribute_to_form(cls, template_path):
        return dict(commitmessage=forms.CharField(
            widget=forms.TextInput(attrs={'size':'100'}),
            label = _('Change message'),
            required = False,
        ))
