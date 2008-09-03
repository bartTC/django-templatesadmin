from django import forms
from templatesadmin.forms import TemplateForm
from templatesadmin import TemplatesAdminException

import subprocess
import os

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

        command = '''git commit %s --author "%s <%s>" -m "Template change, using templatesadmin"''' % (file, author, request.user.email)

        # Stolen from gitpython's git/cmd.py
        proc = subprocess.Popen(args=command, shell=True, cwd=dir, stderr=subprocess.PIPE)

        try:
            stderr_value = proc.stderr.read()
            status = proc.wait()
        finally:
	    proc.stderr.close()

        if status != 0:
            print status
            raise TemplatesAdminException("Error while executing %s: %s" % (command, stderr_value.rstrip(), ))

    @classmethod
    def generate_form(cls, *args, **kwargs):
        return TemplateForm(*args, **kwargs)
