try:
    import json
except:
    import simplejson as json

from django_wizard.wizard import config_index as configs
from django_wizard.models import ConfigOption

MULTIPLE_ANSWERS_PER_USER = ConfigOption(app = 'django_qa',
                                         name = 'MULTIPLE_ANSWERS_PER_USER',
                                         help_text = """If True, each user can answer questions multiple times, else each user can only answer a question once.""",
                                         default = json.dumps(True),
                                         available_options = json.dumps([True, False]),
                                         required = True,
                                         )

ANSWER_OWN_QUESTION = ConfigOption(app = 'django_qa',
                                   name = 'ANSWER_OWN_QUESTION',
                                   help_text = """If True, users can answer their own questions, else self provided answers are not allowed.""",
                                   default = json.dumps(True),
                                   available_options = json.dumps([True, False]),
                                   required = True,
                                   )

MARKDOWN_ENABLED = ConfigOption(app = 'django_qa',
                                name = 'MARKDOWN_ENABLED',
                                help_text = """If True, Markdown markup is enabled for question and answer submission, else Markdown markup is disabled for question and answer submission.""",
                                default = json.dumps(True),
                                available_options = json.dumps([True, False]),
                                required = True,
                                )

CODE_HIGHLIGHTING_ENABLED = ConfigOption(app = 'django_qa',
                                name = 'CODE_HIGHLIGHTING_ENABLED',
                                help_text = """If True, content between <code></code> tags will be highlighted as code, else no highlighting will be provided.""",
                                default = json.dumps(True),
                                available_options = json.dumps([True, False]),
                                required = True,
                                )

CODE_HIGHLIGHTING_LANGUAGE = ConfigOption(app = 'django_qa',
                                name = 'CODE_HIGHLIGHTING_LANGUAGE',
                                help_text = """Determined which language is the default for highlighting content between <code></code> tags.""",
                                default = json.dumps('Python'),
                                available_options = json.dumps(['Python', 'Javascript', 'Ruby', 'C', 'C++', 'Java']),
                                required = True,
                                )

configs.register(MULTIPLE_ANSWERS_PER_USER)
configs.register(ANSWER_OWN_QUESTION)
configs.register(MARKDOWN_ENABLED)
configs.register(CODE_HIGHLIGHTING_ENABLED)
configs.register(CODE_HIGHLIGHTING_LANGUAGE)