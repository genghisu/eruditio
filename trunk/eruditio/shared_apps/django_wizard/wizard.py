from django_wizard.models import ConfigOption, ConfigFixture, DefinedConfigOption
from django.core.exceptions import ObjectDoesNotExist

class ConfigIndex(object):
    def __init__(self):
        self._registry = {}
    
    def register(self, configuration):
        if configuration.__class__ == ConfigOption and not (configuration.app, configuration.name) in self._registry:
            try:
                existing_config = ConfigOption.objects.get(app = configuration.app, name = configuration.name)
            except ObjectDoesNotExist:
                configuration.save()
                existing_config = configuration
            
            try:
                defined_config = DefinedConfigOption.objects.get(option__name = configuration.name, option__app = configuration.app)
            except ObjectDoesNotExist:
                defined_config = DefinedConfigOption(option = existing_config, value = configuration.default)
                defined_config.save()
                
            self._registry[(configuration.app, configuration.name)] = existing_config
            
    def unregister(self, configuration):
        try:
            existing_config = ConfigOption.objects.get(app = configuration.app, name = configuration.name)
            existing_config.delete()
            del self._registry[(configuration.app, configuration.name)]
        except ObjectDoesNotExist:
            pass
    
    def clear_registry(self):
        self._registry = {}
        
config_index = ConfigIndex()

class FixtureIndex(object):
    def __init__(self):
        self._registry = {}
    
    def register(self, fixture):
        if not (fixture.app_label, fixture.module_name) in self._registry:
            try:
                existing_fixture = ConfigFixture.objects.get(app_label = fixture.app_label, module_name = fixture.module_name)
            except ObjectDoesNotExist:
                fixture.save()
                existing_fixture = fixture
                
            self._registry[(fixture.app_label, fixture.module_name)] = fixture
fixtures_index = FixtureIndex()