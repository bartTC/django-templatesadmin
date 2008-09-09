from django import forms

class TemplateForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea()
    )
