import django_relatedcontent.settings as settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from django_relatedcontent.settings import RELATEDCONTENT_LOGGER as logger
import django_relatedcontent.settings as settings

def generate_bind_close_for_target(target_id, data_id, link_class):
    """
    Generate javascript that attaches remove events to the links attached
    to currently selected items. Needed to support none ajax association
    specifically for the creation of new objects.
    """
    vals = {}
    vals['target_id'] = target_id
    vals['link_class'] = link_class
    vals['data_id'] = data_id
    
    script = """<script type='text/javascript'>$("#%(target_id)s > * > .%(link_class)s").live("click",
                function(e) {
                    var metadata = jQuery(this).metadata({type:'attr', name:'data'});
                    var content_type = metadata.content_type;
                    var object_id = metadata.object_id;
                    var ajax_url = metadata.ajax_url;
                    
                    $.remove_from_target("%(target_id)s", content_type, object_id);
                    $.remove_from_data("%(data_id)s", content_type, object_id);
                    
                    return false;
                });
                </script>""" % vals
    script = "\n" + script + "\n"
    return script

def get_template_for_object(object, style = 'default'):
    """
    Template loader for getting the render template to render child objects.
    
    Attempts to check under django_relatedcontent/(app_label)/(model)/(style)
    and falls back to django_relatedcontent/(app_label)/(model)/default.html.
    """
    from django.template.loader import get_template
    from django.template import TemplateDoesNotExist
    
    content_type_object = ContentType.objects.get_for_model(object.__class__)
    object = content_type_object.model_class().objects.get(id = object.id)
    style_template = "django_relatedcontent/%s/%s/%s.html" % (content_type_object.app_label, content_type_object.model, style)
    
    try:
        get_template(style_template)
        target_template = style_template
    except TemplateDoesNotExist, e:
        target_template = "django_relatedcontent/%s/%s/%s.html" % (content_type_object.app_label, content_type_object.model, "default")
    return target_template

def encode_relatedcontent_data(object):
    """
    Encodes related content data for the target object by serializing it
    so that it fits the format expected by the hidden form field which
    contains the current selected items.
    """
    content_type_object = ContentType.objects.get_for_model(object.__class__)
    return "(%s %s)" % (content_type_object.id, object.id)

def persist_get_parameters(url, parameters):
    """
    Attachs query paramaters to an url.
    """
    first = True
    final_url = url
    for key, value in parameters.items():
        if first:
            final_url = "%s?%s=%s" % (final_url, key, value)
            first = False
        else:
            final_url = "%s&%s=%s" % (final_url, key, value)
    return final_url

def generate_relatedcontent_url(base_url, mode, target_id, data_id = None, ajax_associate_url = None):
    """
    Given a base_url, generate a related content url which will determine the properties the child
    items in the thickbox iframe.
    """
    params = {}
    params['base_url'] = base_url
    params['target_id'] = target_id
    params['mode'] = mode
    if mode == getattr(settings, 'UPDATE_MODES')[0]:
        params['data_id'] = data_id
        final_url = """%(base_url)s?target_id=%(target_id)s&data_id=%(data_id)s&mode=%(mode)s""" % params
    elif mode == getattr(settings, 'UPDATE_MODES')[1] or mode == getattr(settings, 'UPDATE_MODES')[2]:
        params['ajax_associate_url'] = ajax_associate_url
        final_url = """%(base_url)s?target_id=%(target_id)s&ajax_associate_url=%(ajax_associate_url)s&mode=%(mode)s""" % params
    return final_url

def generate_thickbox_url(base_url, width, height, iframe = True):
    """
    Give a base_url, generate a thickbox url by attaching the query parameters expected
    by Thickbox.
    """
    params = {}
    params['base_url'] = base_url
    params['width'] = str(width)
    params['height'] = str(height)
    params['TB_iframe'] = str(iframe).lower()
    
    if base_url.find('?') > 0:
        final_url = """%(base_url)s&TB_iframe=%(TB_iframe)s&width=%(width)s&height=%(height)s""" % params
    else:
        final_url = """%(base_url)s?TB_iframe=%(TB_iframe)s&width=%(width)s&height=%(height)s""" % params
    return final_url

def resolve_variable(variable,  context,  default = None):
    """
    Resolve a variable in the context and defaults to @default if it
    cannot be found.
    """
    from django.template import Variable, VariableDoesNotExist

    if not variable[0] == variable[-1] == '"':
        try:
            resolved_variable = Variable(variable).resolve(context)
        except VariableDoesNotExist:
            if default == None:
                resolved_variable = None
            else:
                resolved_variable = default
    else:
        resolved_variable = str(variable[1:-1])
    return resolved_variable

def generate_enable_thickbox(link_id):
    """
    Generate javascript for converting a link to be Thickbox enabled.
    """
    script = """<script type='text/javascript'>tb_init_element("%s");</script>""" % (link_id)
    script = "\n" + script + "\n"
    return script

def parse_relatedcontent_data(data):
    """
    Given encoded related content data form a hidden input field, parse it into
    a list of tuples (content_type, object_id).
    """
    final_data = []
    parts = [x.strip() for x in data.split(",") if x.strip()]
    for part in parts:
        data = part[1:-1].split(" ")
        content_type = data[0]
        object_id = data[1]
        final_data.append((data[0], data[1]))
    return final_data

def render_initial_target(base_object, objects, target_id, data_id, associate_url = None, usage = None):
    """
    Renders the currently associated child objects based on get_template_for_object to
    render the initial state of association.
    """
    from django.template.loader import render_to_string
    from django.conf import settings as project_settings
    
    templates = [render_to_string(get_template_for_object(object), {'base_content_type':ContentType.objects.get_for_model(base_object.__class__).id,
                                                                    'base_object_id':base_object.id,
                                                                    'selectable_object':object, 
                                                                    'selectable_content_type':ContentType.objects.get_for_model(object.__class__).id,
                                                                    'target_id':target_id,
                                                                    'data_id':data_id,
                                                                    'usage':usage,
                                                                    'associate_url':associate_url,
                                                                    'STATIC_URL':getattr(project_settings, 'STATIC_URL', ''), 
                                                                    'MEDIA_URL':getattr(project_settings, 'MEDIA_URL', '')}) for object in objects]
    return "\n".join(templates)
    
class SelectChangeList(object):
    """
    Class representing wrapping a ChangeList object to handle parsing and rendering
    of child objects based on the django admin change_list template.
    """
    UPDATE_MODES = getattr(settings, 'UPDATE_MODES', ('form/js', 'ajax/refresh', 'ajax/update'))
    
    def __init__(self, base_model, base_object_id, selectable_model, usage, request):
        self.base_model = base_model
        self.base_object_id = base_object_id
        self.selectable_model = selectable_model
        self.usage = usage
        self.request = request
        self.admin = self.get_admin(self.selectable_model)
        self.mode = None
        self.target_id = None
        self.data_id = None
        self.ajax_associate_url = None
        
    def parse_query_params(self):
        """
        Attempt to grab the relevant query parameters or initialize them
        to sensible values from a Django request.
        """
        self.target_id = self.request.GET.get('target_id', None)
        self.data_id = self.request.GET.get('data_id', None)
        self.mode = self.request.GET.get('mode', self.__class__.UPDATE_MODES[0])
        self.ajax_associate_url = self.request.GET.get('ajax_associate_url', '')
        
        updated_get = self.request.GET.copy()
        try:
            del updated_get['target_id']
        except KeyError:
            pass
        
        try:
            del updated_get['mode']
        except KeyError:
            pass
        
        try:
            del updated_get['ajax_associate_url']
        except KeyError:
            pass
        
        try:
            del updated_get['data_id']
        except KeyError:
            pass
        
        self.request.GET = updated_get
        status = self.check_mode()
        
        params = {}
        params['target_id'] = self.target_id
        params['mode'] = self.mode
        params['data_id'] = self.data_id
        if self.ajax_associate_url.strip():
            try:
                params['ajax_associate_url'] = reverse(self.ajax_associate_url)
            except:
                params['ajax_associate_url'] = ''
        else:
            params['ajax_associate_url'] = ''
        params['status'] = status
        return params
        
    def check_mode(self):
        """
        Check the current set of query parameters to determine which
        mode is currently being used.  Also error check for possible
        missing values.
        """
        CHECK = True
        if not self.mode in self.__class__.UPDATE_MODES:
            self.mode = self.__class__.UPDATE_MODES[0]
            logger.debug("invalid mode specified, defaulting to %s" % (self.__class__.UPDATE_MODES[0]))
        if self.mode == self.__class__.UPDATE_MODES[0]:
            if not self.target_id:
                logger.debug("for %s a valid target_id needs to be specified" % (self.__class__.UPDATE_MODES[0]))
                CHECK = False
        elif self.mode == self.__class__.UPDATE_MODES[1]:
            if not self.ajax_associate_url:
                logger.debug("for %s a valid ajax_associate_url needs to be specified" % (self.__class__.UPDATE_MODES[1]))
                CHECK = False
        elif self.mode == self.__class__.UPDATE_MODES[2]:
            if not self.ajax_associate_url:
                logger.debug("for %s a valid ajax_associate_url needs to be specified" % (self.__class__.UPDATE_MODES[2]))
                CHECK = False
        return CHECK
            
    def get_admin(self, model):
        """
        Return the ModelAdmin class used by the base model.
        """
        from django.contrib import admin
        
        return admin.site._registry.get(model, None)
    
    def get_related_objects(self):
        """
        Returns a list of integer ids representing all the child objects currently
        associated with the base object.
        """
        from django_relatedcontent.models import ContentAssociation, ContentUsage
        
        try:
            base_object = self.base_model.objects.get(id = self.base_object_id)
            current_related_objects = ContentAssociation.objects.associations_for_object(base_object, self.usage, self.selectable_model)
            related_object_ids = [x.child_object_id for x in current_related_objects]
        except ObjectDoesNotExist:
            related_object_ids = []
        return related_object_ids
    
    def context(self, extra_context = None):
        """
        Generate the context needed by django_relatedcontent/select_change_list.html
        to render a modified change_list template similar to the django.contrib.admin.
        """
        from django.contrib.admin.views.main import ChangeList, ERROR_FLAG
        import django.http as http
        import copy
        
        additional_params = self.parse_query_params()
        current_related_objects = self.get_related_objects()
        
        opts = self.selectable_model._meta
        app_label = opts.app_label
        
        try:
            list_display = copy.deepcopy(self.admin.list_display)
            for field_name in settings.VOID_ADMIN_FIELD_NAMES:
                list_display.remove(field_name)
                
            cl = ChangeList(self.request, 
                            self.admin.model, 
                            list_display, 
                            self.admin.list_display_links, 
                            self.admin.list_filter,
                            self.admin.date_hierarchy,
                            self.admin.search_fields,
                            self.admin.list_select_related,
                            self.admin.list_per_page,
                            self.admin.list_editable,
                            self.admin)
            cl.formset = None
            cl.related_objects = current_related_objects
            cl.title = "Select %s to add" % (opts.verbose_name)
        except Exception, e:
            raise Exception(e)
        
        context = {
            'title': cl.title,
            'is_popup': True,
            'cl': cl,
            'root_path': self.admin.admin_site.root_path,
            'app_label': app_label,
        }
        
        context.update(extra_context or {})
        context.update(additional_params)
        return context

def generate_target_id(content_type, object_id):
    """
    Generate the target area id based on the base object's content_type and id.
    """
    return "%s_%s_%s" % (getattr(settings, 'RELATEDCONTENT_TARGET_PREFIX', ''), str(content_type), str(object_id))

def generate_data_id(content_type, object_id):
    """
    Generate the hidden input id for holding related content data based the base object's
    content_type and id.
    """
    return "%s_%s_%s" % (getattr(settings, 'RELATEDCONTENT_DATA_PREFIX', ''), str(content_type), str(object_id))

def generate_init_id(content_type, object_id):
    """
    Generate the id of the thickbox initialization link based on the base objects' content_type
    and id.
    """
    return "%s_%s_%s" % (getattr(settings, 'RELATEDCONTENT_INIT_PREFIX', ''), str(content_type), str(object_id))