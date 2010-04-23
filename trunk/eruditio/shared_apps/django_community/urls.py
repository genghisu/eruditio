from django.conf.urls.defaults import *

urlpatterns = patterns('django_community.views',
    url(r'^openid_login/', 'openid_login', name='openid-login'),
    url(r'^combined_login/$',  'combined_login',  name='community-combined-login'), 
    url(r'^combined_logout/$',  'combined_logout',  name='community-combined-logout'), 
    url(r'^edit_profile/',  'edit_profile',  name='community-edit-profile'),
    url(r'^profile/(?P<user_id>.+)/(?P<user_name>.*)/$',  'profile',  name='community-profile'),
    url(r'^browse_users/$',  'browse_users',  name='community-browse-users'),
    url(r'^user_required/$',  'user_required',  name='user-required'), 
    url(r'^anonymous_required',  'anonymous_required',  name='anonymous-required'), 
    url(r'^openid_complete/$', 'openid_complete', name='openid-complete'),
    url(r'^contributed_content/(?P<user_id>.+)/(?P<content_type>.+)/', 'contributed_content', name='community-contributed-content'),
    url(r'^modify_favorite/(?P<content_type>.+)/(?P<object_id>.+)/$', 'favorite', name='django-community-favorite'),
    url(r'^standard_login/$', 'standard_login', name='django-community-standard-login'),
    url(r'^standard_signup/$', 'standard_signup', name='django-community-standard-signup'),
)