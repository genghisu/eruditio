try:
    import json
except:
    import simplejson as json
    
import os

from django.core.management.base import NoArgsCommand, CommandError
from django.conf import settings

class ConfigIndex(object):
    def __init__(self):
        self._registry = {}
        
    def register(self, configuration):
         self._registry[(configuration.app, configuration.name)] = configuration

class FixtureIndex(object):
    def __init__(self):
        self._registry = {}
        
    def register(self, configuration):
         pass
         
class Command(NoArgsCommand):
    help = "Initialize app defined configurations used by django_wizard."

    requires_model_validation = False
    can_import_settings = False
    
    def handle_noargs(self, **options):
        from django_wizard.autodiscover import autodiscover
        import django_wizard.wizard
        
        django_wizard.wizard.config_index = ConfigIndex()
        django_wizard.wizard.fixtures_index = FixtureIndex()
        
        autodiscover()
        
        options = django_wizard.wizard.config_index._registry.values()
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
            config_options = [option for option in options if option.app == app]
            for option in config_options:
                config_file.write("%s = %s" % (option.name, output(json.loads(option.default))))
                config_file.write('\n')
