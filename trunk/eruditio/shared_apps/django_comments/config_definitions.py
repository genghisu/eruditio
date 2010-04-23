try:
    import json
except:
    import simplejson as json

from django_wizard.wizard import config_index as configs
from django_wizard.models import ConfigOption

COMMENT_HIDE_THRESHOLD = ConfigOption(app = 'django_comments',
                                      name = 'COMMENT_HIDE_THRESHOLD',
                                      help_text = """Popularity threshold below which comments will be hidden.""",
                                      default = json.dumps(-1),
                                      available_options = json.dumps(''),
                                      required = True,
                                      )

MAX_COMMENTS_PER_DAY = ConfigOption(app = 'django_comments',
                                   name = 'MAX_COMMENTS_PER_DAY',
                                   help_text = """Max number of comments a user is allowed to post per day to avoid spamming.""",
                                   default = json.dumps(20),
                                   available_options =json.dumps(''),
                                   required = True,
                                   )

configs.register(COMMENT_HIDE_THRESHOLD)
configs.register(MAX_COMMENTS_PER_DAY)