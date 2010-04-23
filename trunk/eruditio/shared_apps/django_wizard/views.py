try:
    import json
except:
    import simplejson as json
    
import django.http as http
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from django_wizard.models import DefinedConfigOption, ConfigOption, ConfigFixture

def wizard(request):
    options = ConfigOption.objects.all()
    apps = list(set([option.app for option in options]))
    final_apps = []
    
    for app in apps:
        app_options = options.filter(app = app)
        app_fixtures = ConfigFixture.objects.filter(app_label = app)
        final_apps.append({'name':app, 'options':app_options, 'fixtures':app_fixtures})
    
    return shortcuts.render_to_response('django_wizard/wizard.html',
                                        {'apps':final_apps},
                                        context_instance = RequestContext(request))

def configure_app(request, app_name):
    options = ConfigOption.objects.filter(app = app_name)
    fixtures = ConfigFixture.objects.filter(app_label = app_name)
    
    return shortcuts.render_to_response('django_wizard/app.html',
                                        {'name':app_name,
                                         'options':options,
                                         'fixtures':fixtures},
                                         context_instance = RequestContext(request))

def configure_option(request, option_id):
    from django_wizard.forms import build_config_form
    
    option = ConfigOption.objects.get(id = option_id)
    try:
        defined_option = DefinedConfigOption.objects.get(option = option)
    except ObjectDoesNotExist:
        defined_option = DefinedConfigOption(option = option, value = option.default)
        defined_option.save()
    
    ConfigForm = build_config_form(option, defined_option)
    if request.POST:
        form = ConfigForm(request.POST)
        if form.is_valid():
            defined_option.value = json.dumps(form.cleaned_data['value'])
            defined_option.save()
            return http.HttpResponseRedirect(reverse('django-wizard-main'))
    else:
        form = ConfigForm()
        
    return shortcuts.render_to_response('django_wizard/option.html',
                                        {'option':option,
                                         'defined_option':defined_option,
                                         'form':form},
                                         context_instance = RequestContext(request))

def configure_fixture(request, fixture_id):
    fixture = ConfigFixture.objects.get(id = fixture_id)
    target_url = "/admin/%s/%s" % (fixture.app_label, fixture.module_name)
    
    return http.HttpResponseRedirect(target_url)

def save_configs(request, file = 'base_configuration.json'):
    from django_wizard.utils import save_configs
    
    save_configs(file)
    
    return shortcuts.render_to_response('django_wizard/message.html',
                                        {'message':'Configuration saved as %s' % (file)},
                                        context_instance = RequestContext(request))

def load_configs(request, file = 'base_configuration.json'):
    from django.core.management.commands import loaddata
    from django_wizard.utils import load_configs
    
    load_configs(file)
    
    return shortcuts.render_to_response('django_wizard/message.html',
                                        {'message':'Configuration loaded from %s' % (file)},
                                        context_instance = RequestContext(request))

def load_from(request):
    from django_wizard.utils import list_configs
    
    config_files = list_configs()
    
    return shortcuts.render_to_response('django_wizard/load_from.html',
                                        {'config_files':config_files},
                                        context_instance = RequestContext(request))
    
def save_as(request):
    from django_wizard.forms import SaveAsForm
    from django_wizard.utils import save_configs
    
    if request.POST:
        form = SaveAsForm(request.POST)
        if form.is_valid():
            save_configs(form.cleaned_data['file'])
            return http.HttpResponseRedirect(reverse('django-wizard-main'))
    else:
        form = SaveAsForm()
    
    return shortcuts.render_to_response('django_wizard/save_as.html',
                                        {'form':form},
                                        context_instance = RequestContext(request))

def reset_configs(request):
    from django_wizard.autodiscover import autodiscover
    from django_wizard.wizard import config_index
    
    defined_configs = DefinedConfigOption.objects.all()
    for defined_config in defined_configs:
        defined_config.delete()
        
    configs = ConfigOption.objects.all()
    for config in configs:
        config.delete()
    
    config_index.clear_registry()
    autodiscover()
    return shortcuts.render_to_response('django_wizard/message.html',
                                        {'message':'Configuration have been reset to their default values.'},
                                        context_instance = RequestContext(request))

def generate_configs(request):
    from django_wizard.utils import generate_configs
    
    generate_configs()
    
    return shortcuts.render_to_response('django_wizard/message.html',
                                        {'message':'Configs have been deployed to target apps as config.py.'},
                                        context_instance = RequestContext(request))