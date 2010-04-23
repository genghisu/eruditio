from django.conf.urls.defaults import *

urlpatterns = patterns('core.views',
    url(r'^init/$', 'init', name='core-init'),
    url(r'^contribute/', 'contribute',  name='core-contribute'),
)

urlpatterns += patterns('django_metatagging.views',
    url(r'^objects_with_tag/(?P<content_type>.+)/(?P<tag>.+)/$',  'objects_with_tag',  name='objects-with-tag'),
)