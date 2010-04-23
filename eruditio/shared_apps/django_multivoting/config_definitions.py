try:
    import json
except:
    import simplejson as json

from django_wizard.wizard import config_index as configs
from django_wizard.models import ConfigOption

_CURRENT_APP = 'django_multivoting'

ANONYMOUS_VOTING_ENABLED = ConfigOption(app = _CURRENT_APP,
                                        name = 'ANONYMOUS_VOTING_ENABLED',
                                        help_text = """If True, enables anonymous users cast votes on content.""",
                                        default = json.dumps(True),
                                        available_options = json.dumps([True, False]),
                                        required = True,
                                      )

MAX_VOTES_PER_OBJECT = ConfigOption(app = _CURRENT_APP,
                                   name = 'MAX_VOTES_PER_OBJECT',
                                   help_text = """Determines how many votes each user can cast on each object.""",
                                   default = json.dumps(1),
                                   available_options = json.dumps(''),
                                   required = True,
                                   )

CAN_OWNER_VOTE = ConfigOption(app = _CURRENT_APP,
                                   name = 'CAN_OWNER_VOTE',
                                   help_text = """If True, allows owner of content to vote on said content.""",
                                   default = json.dumps(False),
                                   available_options = json.dumps([True, False]),
                                   required = True,
                                   )

configs.register(ANONYMOUS_VOTING_ENABLED)
configs.register(MAX_VOTES_PER_OBJECT)
configs.register(CAN_OWNER_VOTE)