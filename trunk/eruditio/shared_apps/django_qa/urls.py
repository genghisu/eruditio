from django.conf.urls.defaults import *

urlpatterns = patterns('django_qa.views',
    url(r'^$', 'qa',  name='qa-main'), 
    url(r'^sort/(?P<option>.+)/$',  'qa',  name='qa-sort'), 
    url(r'^sort/(?P<option>.+)/$', 'qa', name='django-qa-list-question'),
    url(r'^sort/(?P<option>.+)/$', 'qa', name='django-qa-list-answer'),
    
    url(r'^ask/$',  'ask',  name='qa-ask'), 
    url(r'^view_question/(?P<question_id>.+)/$',  'view_question',  name='qa-view-question'), 
    url(r'^view_question/(?P<question_id>.+)/$',  'view_question',  name='django-qa-view-question'),
    url(r'^view_answer/(?P<answer_id>.+)/$',  'view_answer',  name='qa-view-answer'), 
    url(r'^view_answer/(?P<answer_id>.+)/$',  'view_answer',  name='django-qa-view-answer'), 
    url(r'^edit_question/(?P<object_id>.+)/$',  'edit_question',  name='qa-edit-question'), 
    url(r'^edit_answer/(?P<object_id>.+)/$',  'edit_answer',  name='qa-edit-answer'), 
    url(r'^accept_answer/(?P<answer_id>.+)/$',  'accept_answer',  name='qa-accept-answer'), 
    url(r'^flag_question/(?P<object_id>.+)/$', 'flag_question', name='qa-flag-question'),
    url(r'^flag_answer/(?P<object_id>.+)/$', 'flag_answer', name = 'qa-flag-answer'),
    url(r'^retag_question/(?P<object_id>.+)/$', 'retag_question', name='qa-retag-question'),
)