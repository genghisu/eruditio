from django.conf.urls.defaults import *

urlpatterns = patterns('django_metatagging.views',
     url(r'^objects_with_tag/(?P<content_type>.+)/(?P<tag>.+)/$',  'objects_with_tag',  name='objects-with-tag'), 
     url(r'^all_objects_with_tag/(?P<tag>.+)/$',  'all_objects_with_tag',  name='all-objects-with-tag'), 
     
     url(r'^browse/$',  'browse',  name='browse-tags'), 
     url(r'^browse_ajax/(?P<tag>.+)/$',  'browse_ajax',  name='browse-tags-ajax'), 
     url(r'^browse_ajax/$',  'browse_ajax',  name='browse-tags-ajax-placeholder'),
)