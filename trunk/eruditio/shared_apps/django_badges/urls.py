from django.conf.urls.defaults import *

urlpatterns = patterns('django_badges.views',
    url(r'^view/(?P<badge_id>.+)/', 'view',  name='django-badges-view'),
    url(r'^browse/', 'browse',  name='django-badges-browse'), 
)