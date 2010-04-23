from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
import django_lazyload as lazyload

admin.autodiscover()
lazyload.autodiscover()

urlpatterns = patterns('',
    url(r'^$',  'core.views.main',  name='main'), 
    (r'^core/',  include('core.urls')), 
    (r'^info/', include('info.urls')),
    (r'^app/', include('applications.urls')),
    (r'^projects/', include('projects.urls')),
    (r'^code/', include('code.urls')),
    (r'^tutorials/', include('tutorials.urls')),
    (r'^qa/', include('django_qa.urls')),
    (r'^community/', include('django_community.urls')),
    (r'^vote/', include('django_multivoting.urls')),
    (r'^comment/', include('django_comments.urls')),
    (r'^moderate/', include('django_moderation.urls')),
    (r'^tags/', include('django_metatagging.urls')),
    (r'^related_content/', include('django_relatedcontent.urls')),
    (r'^reputation/', include('django_reputation.urls')),
    (r'^history/', include('django_contenthistory.urls')),
    (r'^badges/', include('django_badges.urls')),
    (r'^search/', include('search.urls')),
    (r'^wizard/', include('django_wizard.urls')),
    (r'^common/', include('django_common.urls')),
    (r'^admin/(.*)', admin.site.root),
)

handler500 = 'django.views.defaults.server_error',
handler404 = 'django.views.defaults.page_not_found'

if getattr(settings, 'LOCAL_DEV_SERVER', None):
    from urlparse import urlsplit    
    url = urlsplit(settings.MEDIA_URL).path[1:]
    root = settings.MEDIA_ROOT
    urlpatterns += patterns('django.views.static',
        (r'^%s(?P<path>.*)$' % url, 'serve', {'document_root': root, 'show_indexes': True}),
    )
    url = urlsplit(settings.STATIC_URL).path[1:]
    root = settings.STATIC_ROOT
    urlpatterns += patterns('django.views.static',
        (r'^%s(?P<path>.*)$' % url, 'serve', {'document_root': root, 'show_indexes': True}),
    )
    url = urlsplit(settings.STATIC_LOCAL_URL).path[1:]
    root = settings.STATIC_LOCAL_ROOT
    urlpatterns += patterns('django.views.static',
        (r'^%s(?P<path>.*)$' % url, 'serve', {'document_root': root, 'show_indexes': True}),
    )
    (r'^favicon', None),
