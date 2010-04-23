from django.conf.urls.defaults import *

urlpatterns = patterns('django_multivoting.views',
    url(r'^vote/(?P<content_type>.+)/(?P<object_id>.+)/(?P<vote_mode>.+)/(?P<template_mode>.+)/$',  'vote',  name='vote'), 
)