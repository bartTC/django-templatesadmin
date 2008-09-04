from django import forms
from django.utils.translation import ugettext_lazy

class TemplateForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea()
    )
    backup = forms.BooleanField(
        label = ugettext_lazy(u'Backup file before saving?'),
        required = False,
    )
    