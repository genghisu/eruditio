try:
    import json
except:
    import simplejson as json

from django_wizard.wizard import config_index as configs
from django_wizard.models import ConfigOption

_CURRENT_APP = 'django_openidconsumer'

BASE_URI = ConfigOption(app = _CURRENT_APP,
                        name = 'BASE_URI',
                        help_text = """Base url of OpenID schema.""",
                        default = json.dumps('http://axschema.org'),
                        available_options = json.dumps([True, False]),
                        required = True,
                        )

URI_GROUPS = ConfigOption(app = _CURRENT_APP,
                           name = 'URI_GROUPS',
                           help_text = """Lookup dict for generating canonical urls for OpenID schema attributes.""",
                           default = json.dumps({'alias':{"type_uri":"%s%sfriendly" % ('http://axschema.org/', 'namePerson/'),
                                                          "alias":"alias",
                                                          "required":True,
                                                          "count":1}, 
                                                 'email':{"type_uri":"%s%s" % ('http://axschema.org/', 'contact/email'),
                                                            "alias":"email",
                                                            "required":True,
                                                            "count":1
                                                            },
                                                          }),
                           available_options = json.dumps(''),
                           required = True,
                           )

OPENID_PAPE = ConfigOption(app = _CURRENT_APP,
                                   name = 'OPENID_PAPE',
                                   help_text = """If True, enables usage of the Pape extension.""",
                                   default = json.dumps(False),
                                   available_options = json.dumps([True, False]),
                                   required = True,
                                   )

OPENID_SREG = ConfigOption(app = _CURRENT_APP,
                                   name = 'OPENID_SREG',
                                   help_text = """If True, enables usage of the Simple Registration extension.""",
                                   default = json.dumps(False),
                                   available_options = json.dumps([True, False]),
                                   required = True,
                                   )

OPENID_AX = ConfigOption(app = _CURRENT_APP,
                                   name = 'OPENID_AX',
                                   help_text = """If True, enables usage of the AX extension.""",
                                   default = json.dumps(True),
                                   available_options = json.dumps([True, False]),
                                   required = True,
                                   )

configs.register(BASE_URI)
configs.register(URI_GROUPS)
configs.register(OPENID_PAPE)
configs.register(OPENID_SREG)
configs.register(OPENID_AX)