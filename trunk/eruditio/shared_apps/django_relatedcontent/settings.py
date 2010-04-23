import logging
from django.conf import settings

RELATEDCONTENT_LOGGER = logging.getLogger('django_relatedcontent')

RELATEDCONTENT_PREFIX = getattr(settings, 'RELATEDCONTENT_PREFIX', 'relatedcontent')
RELATEDCONTENT_TARGET_PREFIX = "%s_%s" % (RELATEDCONTENT_PREFIX, 'target')
RELATEDCONTENT_DATA_PREFIX = "%s_%s" % (RELATEDCONTENT_PREFIX, 'data')
RELATEDCONTENT_INIT_PREFIX = "%s_%s" % (RELATEDCONTENT_PREFIX, 'init')

RELATEDCONTENT_FIELD_CLASS = "%s_%s" % (RELATEDCONTENT_PREFIX, 'field')
DEFAULT_CHANGE_LIST_TEMPLATE = getattr(settings, 'DEFAULT_CHANGE_LIST_TEMPLATE', 'django_relatedcontent/select_change_list.html')
VOID_ADMIN_FIELD_NAMES = getattr(settings, 'VOID_ADMIN_FIELDS', ['action_checkbox'])

INVALID_HANDLER = 1
ERROR_CODES = \
{1: 'invalid handler'}

UPDATE_MODES = ('form/js', 'ajax/refresh', 'ajax/update')