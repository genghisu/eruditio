from django.conf.urls.defaults import *

urlpatterns = patterns('django_wizard.views',
    url(r'^$', 'wizard',  name='django-wizard-main'), 
    url(r'^configure_app/(?P<app_name>.+)/$', 'configure_app',  name='django-wizard-configure-app'), 
    url(r'^configure_option/(?P<option_id>.+)/$', 'configure_option',  name='django-wizard-configure-option'), 
    url(r'^configure_fixture/(?P<fixture_id>.+)/$', 'configure_fixture',  name='django-wizard-configure-fixture'),
    url(r'^save_configs/(?P<file>.+)/$', 'save_configs',  name='django-wizard-save-configs'), 
    url(r'^load_configs/(?P<file>.+)/$', 'load_configs',  name='django-wizard-load-configs'), 
    url(r'^reset_configs/$', 'reset_configs',  name='django-wizard-reset-configs'),
    url(r'^generate_configs/$', 'generate_configs',  name='django-wizard-generate-configs'),
    url(r'^load_from/$', 'load_from',  name='django-wizard-load-from'),
    url(r'^save_as/$', 'save_as',  name='django-wizard-save-as'), 
)