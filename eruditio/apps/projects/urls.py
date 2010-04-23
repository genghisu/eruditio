from django.conf.urls.defaults import *

urlpatterns = patterns('projects.views',
    url(r'^contribute/$', 'contribute', name='projects-contribute'),
    url(r'^view/$', 'view', name='projects-view-project'),
    url(r'^project_list/(?P<option>.+)/$', 'projects_list', name='projects-list'),
)