try:
    import json
except:
    import simplejson as json

from django_wizard.wizard import config_index as configs
from django_wizard.models import ConfigOption

_CURRENT_APP = 'django_community_wiki'

COMMUNITY_WIKI_VOTE_LIMIT = ConfigOption(app = _CURRENT_APP,
                                         name = 'COMMUNITY_WIKI_VOTE_LIMIT',
                                         help_text = """Number of up votes above which an object will be owned by the community_wiki user""",
                                         default = json.dumps(25),
                                         available_options = json.dumps(''),
                                         required = True,
                                      )

COMMUNITY_WIKI_POPULARITY_LIMIT = ConfigOption(app = _CURRENT_APP,
                                   name = 'COMMUNITY_WIKI_POPULARITY_LIMIT',
                                   help_text = """Lower threshold of popularity below which an object will be owned by the community_wiki.""",
                                   default = json.dumps(-7),
                                   available_options = json.dumps(''),
                                   required = True,
                                   )

configs.register(COMMUNITY_WIKI_VOTE_LIMIT)
configs.register(COMMUNITY_WIKI_POPULARITY_LIMIT)