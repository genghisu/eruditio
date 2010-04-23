try:
    import json
except:
    import simplejson as json

from django_wizard.wizard import config_index as configs
from django_wizard.wizard import fixtures_index as fixtures
from django_wizard.models import ConfigOption, ConfigFixture

_CURRENT_APP = 'django_moderation'

ANONYMOUS_APPROVAL_ENABLED = ConfigOption(app = _CURRENT_APP,
                                      name = 'ANONYMOUS_APPROVAL_ENABLED',
                                      help_text = """If True, enables anonymous users to approve content.""",
                                      default = json.dumps(True),
                                      available_options = json.dumps([True, False]),
                                      required = True,
                                      )

DEFAULT_FLAG_VOTE_WEIGHT = ConfigOption(app = _CURRENT_APP,
                                   name = 'DEFAULT_FLAG_VOTE_WEIGHT',
                                   help_text = """Default value for the weight of a ContentFlagVote.  Used in conjunction with FLAG_VOTE_THRESHOLD.""",
                                   default = json.dumps(1),
                                   available_options = json.dumps(''),
                                   required = True,
                                   )

FLAG_VOTE_THRESHOLD = ConfigOption(app = _CURRENT_APP,
                                   name = 'FLAG_VOTE_THRESHOLD',
                                   help_text = """Once the total weight of ContentFlagVotes for a particular flag on an object goes over this threshold, the flag will be set on the target object.""",
                                   default = json.dumps(5),
                                   available_options = json.dumps(''),
                                   required = True,
                                   )

DEFAULT_REASONS = ConfigOption(app = _CURRENT_APP,
                                   name = 'DEFAULT_REASONS',
                                   help_text = """Reasons that users can use with casting ContentFlagVotes.""",
                                   default = json.dumps({'offensive':('offensive', 'contains offensive content'),
                                                         'invalid': ('incorrect', 'contains invalid, deprecated or incorrect information'),
                                                         'advertising':('advertising', 'contains blatant advertising'),
                                                         'duplicate':('duplicate', 'is a duplicate'),
                                                         'unrelated':('unrelated', 'does not contain relevant content'),
                                                         'unclear':('unclear', 'poorly written or unclear')
                                                        }),
                                   available_options = json.dumps(''),
                                   required = True,
                                   )

MODERATE_FLAG = ConfigOption(app = _CURRENT_APP,
                             name = 'MODERATE_FLAG',
                             help_text = """Predefined ContentFlag which flags an object for moderation""",
                             default = json.dumps('IN_MODERATION'),
                             available_options = json.dumps(''),
                             required = True
                             )

ContentFlagFixture = ConfigFixture(help_text = 'Configure content flags that can be set on objects.',
                                   app_label = _CURRENT_APP,
                                   module_name = 'contentflag')

ReasonFixture = ConfigFixture(help_text = 'Configure the reasons that users can provide when flagging content',
                              app_label = _CURRENT_APP,
                              module_name = 'reason')

ModeratedContentFixture = ConfigFixture(help_text = 'Configure which content will undergo a moderation process before shown on the site.',
                                        app_label = _CURRENT_APP,
                                        module_name = 'moderatedcontent')

fixtures.register(ContentFlagFixture)
fixtures.register(ReasonFixture)
fixtures.register(ModeratedContentFixture)

configs.register(ANONYMOUS_APPROVAL_ENABLED)
configs.register(DEFAULT_FLAG_VOTE_WEIGHT)
configs.register(FLAG_VOTE_THRESHOLD)
configs.register(DEFAULT_REASONS)