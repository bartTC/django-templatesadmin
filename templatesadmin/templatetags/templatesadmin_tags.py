from base64 import urlsafe_b64encode
from django import template

register = template.Library()

@register.filter
def base64urlencode(url):
    return urlsafe_b64encode(url)
