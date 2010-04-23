from django.conf.urls.defaults import *

urlpatterns = patterns('django_contenthistory.views',
    url(r'^history/(?P<content_type>.+)/(?P<object_id>.+)/$', 'history',  name='django-contenthistory-history'),
)
