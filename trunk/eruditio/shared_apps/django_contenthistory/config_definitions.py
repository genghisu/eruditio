try:
    import json
except:
    import simplejson as json

from django_wizard.wizard import config_index as configs
from django_wizard.wizard import fixtures_index as fixtures
from django_wizard.models import ConfigOption, ConfigFixture

TrackedContentFixture = ConfigFixture(help_text = 'Configure the models that will have their histories tracked by django_contenthistory.',
                                      app_label = 'django_contenthistory',
                                      module_name = 'trackedcontent')

ModelFieldFixture = ConfigFixture(help_text = 'Configure the fields for each TrackedContent object that will be tracked',
                                  app_label = 'django_contenthistory',
                                  module_name = 'modelfield')

fixtures.register(TrackedContentFixture)
fixtures.register(ModelFieldFixture)