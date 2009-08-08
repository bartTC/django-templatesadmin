from templatesadmin.forms import TemplateForm

class TemplatesAdminHook(object):
    '''
    Hook baseclass
    '''

    @classmethod
    def pre_save(cls, request, form, template_path):
        pass

    @classmethod
    def post_save(cls, request, form, template_path):
        pass

    @classmethod
    def contribute_to_form(cls, form, template_path):
        return form
