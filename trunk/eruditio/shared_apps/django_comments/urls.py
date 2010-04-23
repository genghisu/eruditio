from django.conf.urls.defaults import *

urlpatterns = patterns('django_comments.views', 
    url(r'^ajax_comment/(?P<content_type>.+)/(?P<object_id>.+)/(?P<comment_class>.+)/$',  'ajax_comment',  name='ajax-comment'), 
    url(r'^edit_comment/(?P<comment_id>.+)/$',  'edit_comment',  name='edit-comment'), 
    url(r'^comments/(?P<content_type>.+)/(?P<object_id>.+)/(?P<comment_class>.+)/$',  'list',  name='django-comments-list'), 
)
