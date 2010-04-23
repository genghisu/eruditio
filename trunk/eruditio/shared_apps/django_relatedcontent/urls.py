from django.conf.urls.defaults import *

urlpatterns = patterns('django_relatedcontent.views',
    url(r'^select/(?P<base_content_type>.+)/(?P<base_object_id>.+)/(?P<usage>.+)/$',  'select_main',  name='django-relatedcontent-select'),
    
    url(r'^select_from_content_type/(?P<base_content_type>.+)/(?P<base_object_id>.+)/(?P<selectable_content_type>.+)/(?P<usage>.+)/$', 'select_change_list', name='django-relatedcontent-content-select'),
    
    url(r'^select_error/(?P<select_error>.+)/$', 'select_error', name='django-relatedcontent-error'), 
    
    url(r'^modify_content_association/$', 'modify_content_association', name='django-relatedcontent-modify-association'),
    
    url(r'^render_content_item/$', 'render_content_item', name='django-relatedcontent-render-item'),
)