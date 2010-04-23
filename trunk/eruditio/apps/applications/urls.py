from django.conf.urls.defaults import *

urlpatterns = patterns('applications.views',
    url(r'^$', 'apps_list',  name='applications-main'), 
    url(r'^contribute_app/$', 'contribute_app', name='applications-contribute-app'),
    url(r'^view_app/(?P<app_id>.+)/$', 'view_app', name='applications-view-app'),
    url(r'^apps_list/(?P<option>.+)/$', 'apps_list', name='applications-list-app'),
    url(r'^flag_app/(?P<object_id>.+)/$', 'flag_app', name='applications-flag-app'),
    url(r'^edit_app/(?P<object_id>.+)/$', 'edit_app', name='applications-edit-app'),
    url(r'^retag_app/(?P<object_id>.+)/$', 'retag_app', name='applications-retag-app'),
    url(r'^edit_app_dependencies/(?P<app_id>.+)/$', 'edit_dependencies', name='applications-edit-app-dependencies'),
)