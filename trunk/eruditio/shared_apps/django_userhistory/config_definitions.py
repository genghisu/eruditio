try:
    import json
except:
    import simplejson as json

from django_wizard.wizard import config_index as configs
from django_wizard.wizard import fixtures_index as fixtures
from django_wizard.models import ConfigOption, ConfigFixture

_CURRENT_APP = 'django_userhistory'

UserActionFixture = ConfigFixture(help_text = 'Configure the user actions that will be tracked.',
                                  app_label = _CURRENT_APP,
                                  module_name = 'useraction')

UserTrackedContentFixture = ConfigFixture(help_text = """Configure content that when saved will be attributed to an user's history of actions.""",
                                          app_label = _CURRENT_APP,
                                          module_name = 'usertrackedcontent')

fixtures.register(UserActionFixture)
fixtures.register(UserTrackedContentFixture)