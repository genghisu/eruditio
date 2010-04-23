from django.conf.urls.defaults import *

urlpatterns = patterns('django_moderation.views',
    url(r'^moderate/(?P<content_type>.+)/(?P<object_id>.+)/(?P<mode>.+)/$', 'moderate', name='moderation-moderate'),
    url(r'^queue/$', 'queue',  name='moderation-queue'), 
    url(r'^queue/(?P<content_type>.+)/$', 'queue',  name='moderation-queue-single'),
    url(r'^delete/(?P<content_type>.+)/(?P<object_id>.+)/$', 'delete',  name='django-moderation-delete'), 
)