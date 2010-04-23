from django.conf import settings

MULTIPLE_ANSWERS_PER_USER = getattr(settings, 'MULTIPLE_ANSWERS_PER_USER', False)
ANSWER_OWN_QUESTION = getattr(settings, 'ANSWER_OWN_QUESTION', False)

MARKDOWN_ENABLED = getattr(settings, 'MARKDOWN_ENABLED', True)
CODE_HIGHLIGHTING_ENABLED = getattr(settings, 'CODE_HIGHLIGHTING_ENABLED', True)
CODE_HIGHLIGHTING_LANGUAGE = getattr(settings, 'CODE_HIGHLIGHTING_LANGUAGE', 'python')