import os
import pprint

try:
    import json
except:
    import simplejson as json
    
from django_wizard.models import ConfigFixture, ConfigOption, DefinedConfigOption
from django.db.models import get_model
from django.core import serializers
from django.conf import settings

def save_configs(file):
    objects = []
    config_fixtures = ConfigFixture.objects.all()
    target_models = [get_model(fixture.app_label, fixture.module_name) for fixture in config_fixtures]
    for model in target_models:
        objects.extend(model.objects.all())
        
    objects.extend(ConfigFixture.objects.all())
    objects.extend(ConfigOption.objects.all())
    objects.extend(DefinedConfigOption.objects.all())
    
    data = serializers.serialize('json', objects, indent=None)
    target_file = open(os.path.join(settings.PROJECT_ROOT, 'django_wizard_configurations', file), 'w+')
    target_file.write(data)
    
def load_configs(file):
    try:
        loaddata.Command().execute(os.path.join(settings.PROJECT_ROOT, 'django_wizard_configurations', file), verbosity = 0)
    except:
        pass

def list_configs():
    return os.listdir(os.path.join(settings.PROJECT_ROOT, 'django_wizard_configurations'))

def generate_configs(override_options = None):
    options = ConfigOption.objects.all()
    apps = list(set([option.app for option in options]))
    
    def output(value):
            if value.__class__ in [str, unicode]:
                return """'%s'""" % (value)
            else:
                return str(value)
        
    for app in apps:
        app_module = __import__(app)
        app_dir = os.path.dirname(app_module.__file__)
        config_file = open(os.path.join(app_dir, 'config.py'), 'w+')
        config_options = DefinedConfigOption.objects.filter(option__app = app)
        for option in config_options:
            config_file.write("%s = %s" % (option.option.name, output(json.loads(option.value))))
            config_file.write('\n')
            