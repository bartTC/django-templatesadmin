from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'templatesadmin.views.listing', name='templatesadmin-overview'),
    url(r'^edit(?P<path>.*)/$', 'templatesadmin.views.modify', name='templatesadmin-edit'),
)
