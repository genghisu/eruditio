try:
    import json
except:
    import simplejson as json

from django_wizard.wizard import config_index as configs
from django_wizard.wizard import fixtures_index as fixtures
from django_wizard.models import ConfigOption, ConfigFixture

_CURRENT_APP = 'django_relatedcontent'

RELATEDCONTENT_PREFIX = ConfigOption(app = _CURRENT_APP,
                                     name = 'RELATEDCONTENT_PREFIX',
                                     help_text = """Prefix for dom level elements that are used by django_relatedcontent.""",
                                     default = json.dumps('relatedcontent'),
                                     available_options = json.dumps(''),
                                     required = True,
                        )

RELATEDCONTENT_TARGET_PREFIX = ConfigOption(app = _CURRENT_APP,
                                            name = 'RELATEDCONTENT_TARGET_PREFIX',
                                            help_text = """Prefix for target elements (where associated content gets displayed).""",
                                            default = json.dumps('relatedcontent_target'),
                                            available_options = json.dumps(''),
                                            required = True,
                           )

RELATEDCONTENT_DATA_PREFIX = ConfigOption(app = _CURRENT_APP,
                                           name = 'RELATEDCONTENT_DATA_PREFIX',
                                           help_text = """Prefix for data elements (hidden input field where associated element ids are stored).""",
                                           default = json.dumps('relatedcontent_data'),
                                           available_options = json.dumps(''),
                                           required = True,
                                           )

RELATEDCONTENT_INIT_PREFIX = ConfigOption(app = _CURRENT_APP,
                                          name = 'RELATEDCONTENT_INIT_PREFIX',
                                          help_text = """Prefix for <a> tags which initiates the selection thickbox iframe.""",
                                          default = json.dumps('relatedcontent_init'),
                                          available_options = json.dumps(''),
                                          required = True,
                                   )

RELATEDCONTENT_FIELD_CLASS = ConfigOption(app = _CURRENT_APP,
                                          name = 'RELATEDCONTENT_FIELD_CLASS',
                                          help_text = """CSS class associated with the default RelatedContentField.""",
                                          default = json.dumps('relatedcontent_field'),
                                          available_options = json.dumps(''),
                                          required = True,
                                   )

DEFAULT_CHANGE_LIST_TEMPLATE = ConfigOption(app = _CURRENT_APP,
                                              name = 'DEFAULT_CHANGE_LIST_TEMPLATE',
                                              help_text = """Template to use for rendering the selection changelist when an override has not been provided.""",
                                              default = json.dumps('django_relatedcontent/selected_change_list.html'),
                                              available_options = json.dumps(''),
                                              required = True,
                                   )

VOID_ADMIN_FIELD_NAMES = ConfigOption(app = _CURRENT_APP,
                                      name = 'VOID_ADMIN_FIELD_NAMES',
                                      help_text = """Field names which should be removed from the default rendering of ChangeList since they are not used by django_relatedcontent.""",
                                      default = json.dumps(['action_checkbox']),
                                      available_options = json.dumps(''),
                                      required = True,
                                   )

UPDATE_MODES = ConfigOption(app = _CURRENT_APP,
                              name = 'UPDATE_MODES',
                              help_text = """Modes of operation for django_relatedcontent.  Determines how content gets associated.  In form/js mode, when an object is associated, it will be
rendered inside the related target dom element and data will be added to the relatedcontent data dom element.  This mode is useful for creating new objects when the primary id of the primary object
has not been determined.  Modes ajax/refresh and ajax/update can be used when an add action or remove action needs to immediately update the database.  These modes are useful when dealing
with objects that have already been created.""",
                              default = json.dumps(['action_checkbox']),
                              available_options = json.dumps(''),
                              required = True,
                            )

configs.register(RELATEDCONTENT_PREFIX)
configs.register(RELATEDCONTENT_TARGET_PREFIX)
configs.register(RELATEDCONTENT_DATA_PREFIX)
configs.register(RELATEDCONTENT_INIT_PREFIX)
configs.register(RELATEDCONTENT_FIELD_CLASS)

configs.register(DEFAULT_CHANGE_LIST_TEMPLATE)
configs.register(VOID_ADMIN_FIELD_NAMES)
configs.register(UPDATE_MODES)

ContentUsageFixture = ConfigFixture(help_text = 'Configure the modes of content usage that determine the type of associations between related objects.',
                                    app_label = _CURRENT_APP,
                                    module_name = 'contentusage')

AvailableContentUsageFixture = ConfigFixture(help_text = 'Configure the possible relationships available between content',
                                             app_label = _CURRENT_APP,
                                             module_name = 'availablecontentusage')


fixtures.register(ContentUsageFixture)
fixtures.register(AvailableContentUsageFixture)