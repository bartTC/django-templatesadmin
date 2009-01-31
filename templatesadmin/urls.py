from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'templatesadmin.views.overview', name='templatesadmin-overview'),
    url(r'^edit(?P<path>.*)/$', 'templatesadmin.views.edit', name='templatesadmin-edit'),
)
