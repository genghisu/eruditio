from django.conf.urls.defaults import *

urlpatterns = patterns('code.views',
    url(r'^$', 'code_list',  name='code-main'), 
    url(r'^contribute/$', 'contribute_code', name='code-contribute-code'),
    url(r'^view/(?P<code_id>.+)/$', 'view', name='code-view'),
    url(r'^view/(?P<code_id>.+)/$', 'view', name='code-view-code'),
    url(r'^view_full/(?P<code_id>.+)/$', 'view_full', name='code-view-code-full'),
    url(r'^code_list/(?P<option>.+)/$', 'code_list', name='code-list'),
    url(r'^code_list/(?P<option>.+)/$', 'code_list', name='code-list-code'),
    url(r'^flag_code/(?P<object_id>.+)/$', 'flag_code', name='code-flag'),
    url(r'^code_list/(?P<option>.+)/$', 'code_list', name='code-sort'),
    url(r'^edit_code/(?P<object_id>.+)/$', 'edit_code', name='code-edit'),
    url(r'^retag_code/(?P<object_id>.+)/$', 'retag_code', name='code-retag'),
)