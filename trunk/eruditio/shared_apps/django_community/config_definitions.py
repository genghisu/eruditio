try:
    import json
except:
    import simplejson as json

from django_wizard.wizard import config_index as configs
from django_wizard.models import ConfigOption

_CURRENT_APP = 'django_community'

OPENID_FIELD_MAPPING = ConfigOption(app = _CURRENT_APP,
                                      name = 'OPENID_FIELD_MAPPING',
                                      help_text = """OpenID field name mappings from http://openid.net/specs/openid-authentication-2_0.html to django_community.models.UserProfile fields.""",
                                      default = json.dumps({'nickname' : 'display_name',
                                                             'email' : 'email',
                                                             'fullname' : 'fullname',
                                                             'dob' : 'birthdate',
                                                             'country' : 'location'}),
                                      available_options = json.dumps(''),
                                      required = True,
                                      )

OPENID_ENABLED = ConfigOption(app = _CURRENT_APP,
                                   name = 'OPENID_ENABLED',
                                   help_text = """If True, allows login via OpenID.""",
                                   default = json.dumps(True),
                                   available_options = json.dumps([True, False]),
                                   required = True,
                                   )

ANONYMOUS_USERS_ENABLED = ConfigOption(app = _CURRENT_APP,
                                   name = 'ANONYMOUS_USERS_ENABLED',
                                   help_text = """If True, enables middleware which creates uniquely identified anonymous django.contrib.auth.models.User objects.  Useful for letting anonmyous users access to community tools which need to attach an User object via a ForeignKey.""",
                                   default = json.dumps(False),
                                   available_options = json.dumps([True, False]),
                                   required = True,
                                   )

PROFILE_TEMPLATE = ConfigOption(app = _CURRENT_APP,
                                   name = 'PROFILE_TEMPLATE',
                                   help_text = """Template that should be used to display user profiles.""",
                                   default = json.dumps('django_community/profile.html'),
                                   available_options = json.dumps(''),
                                   required = True,
                                   )

PROFILES_ENABLED = ConfigOption(app = _CURRENT_APP,
                                name = 'PROFILES_ENABLED',
                                help_text = """If True, enables a view for displaying user profile data.""",
                                default = json.dumps(True),
                                available_options = json.dumps([True, False]),
                                required = True,
                                )

configs.register(OPENID_FIELD_MAPPING)
configs.register(OPENID_ENABLED)
configs.register(ANONYMOUS_USERS_ENABLED)
configs.register(PROFILES_ENABLED)
configs.register(PROFILE_TEMPLATE)