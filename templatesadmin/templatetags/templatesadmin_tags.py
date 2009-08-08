from os import path
from django.template import Library

register = Library()

@register.filter
def shortenfilepath(path, num_dirs=2, pathsep='/'):
    splitted = path.split(path)[1]
    return pathsep.join(path.split(pathsep)[-num_dirs:])
