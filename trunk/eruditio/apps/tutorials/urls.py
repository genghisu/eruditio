from django.conf.urls.defaults import *

urlpatterns = patterns('tutorials.views',
    url(r'^$', 'tutorials_list',  name='tutorials-main'), 
    url(r'^contribute/$', 'contribute_tutorial', name='tutorials-contribute-tutorial'),
    url(r'^view/(?P<tutorial_id>.+)/$', 'view', name='tutorials-view-tutorial'),
    url(r'^tutorials_list/(?P<option>.+)/$', 'tutorials_list', name='tutorials-list-tutorial'),
    url(r'^flag_tutorial/(?P<object_id>.+)/$', 'flag_tutorial', name='tutorials-flag-tutorial'),
    url(r'^edit_tutorial/(?P<object_id>.+)/$', 'edit_tutorial', name='tutorials-edit-tutorial'),
    url(r'^retag_tutorial/(?P<object_id>.+)/$', 'retag_tutorial', name='tutorials-retag-tutorial'),
)