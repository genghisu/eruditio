"""
Configurations definitions for this module to the specs od django-config-wizard.
"""

try:
    import json
except:
    import simplejson as json

from django_wizard.wizard import config_index as configs
from django_wizard.wizard import fixtures_index as fixtures
from django_wizard.models import ConfigOption, ConfigFixture

BadgeFixture = ConfigFixture(help_text = 'Configure the Badges that are available to the users of this site.',
                             app_label = 'django_badges',
                             module_name = 'badge')

fixtures.register(BadgeFixture)