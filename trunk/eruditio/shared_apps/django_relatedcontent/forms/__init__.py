from django.forms.widgets import Widget
from django.forms.fields import Field
from django.utils.safestring import mark_safe
from django.utils.encoding import StrAndUnicode, force_unicode
from django.forms.util import flatatt
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.conf import settings as project_settings

from django_relatedcontent.utils import (generate_enable_thickbox, generate_relatedcontent_url, generate_thickbox_url,
                                        encode_relatedcontent_data, get_template_for_object, generate_bind_close_for_target,
                                        generate_target_id, generate_data_id, generate_init_id, render_initial_target)
import django_relatedcontent.settings as settings
from django_relatedcontent.models import ContentAssociation

class RelatedContentWidget(Widget):
    """
    Widget which generates a set of form elements denoting a target area for rendering selected objects,
    a hidden input for holding the current set of selected objects and a link for initiating the thickbox
    iframe which contains the selection change_list.
    """
    input_type = 'relatedcontent'
    
    def render(self, name, value, attrs = None):
        if value is None: 
            value = ''
        final_attrs = self.build_attrs(attrs, type = self.input_type, name = name)
        if value != '':
            final_attrs['value'] = force_unicode(value)
        else:
            final_attrs['value'] = ''
        
        target_id = generate_target_id(final_attrs['base_content_type'], final_attrs['base_object_id'])
        data_id = generate_data_id(final_attrs['base_content_type'], final_attrs['base_object_id'])
        init_id = generate_init_id(final_attrs['base_content_type'], final_attrs['base_object_id'])
        element_class = "%s %s" % (final_attrs.get('class', ''), getattr(settings, 'RELATEDCONTENT_FIELD_CLASS', ''))
        
        target_attrs = {}
        target_attrs['id'] = target_id
        target_attrs['class'] = element_class
        
        data_attrs = {}
        data_attrs['id'] = data_id
        data_attrs['type'] = 'hidden'
        data_attrs['class'] = element_class
        data_attrs['value'] = self.get_initial_data(final_attrs['initial_data'])
        data_attrs['name'] = final_attrs['name']
        
        init_attrs = {}
        init_attrs['id'] = init_id
        init_attrs['class'] = element_class
        
        relatedcontent_url = generate_relatedcontent_url(base_url = final_attrs['base_url'], 
                                                  mode = getattr(settings, 'UPDATE_MODES')[0],
                                                  target_id = target_id,
                                                  data_id = data_id)
        target_url = generate_thickbox_url(relatedcontent_url, final_attrs['iframe_width'], final_attrs['iframe_height'])
        
        initial_target = self.get_initial_target(final_attrs['base_object'], 
                                                 final_attrs['initial_data'], 
                                                 target_id, 
                                                 data_id)
        
        target = u"""<div%s>%s</div>""" % (flatatt(target_attrs), initial_target)
        data = u"""<input%s></input>""" % flatatt(data_attrs)
        init = u"""<a href='%s' %s>Select</a>""" % (target_url, flatatt(init_attrs))
        thickbox_script = generate_enable_thickbox(init_id)
        bind_click_script = ""
        
        return mark_safe(target + "\n" + data + "\n" + init + "\n" + thickbox_script + "\n" + bind_click_script)
    
    def get_initial_target(self, base_object, objects, target_id, data_id):
        from django.template.loader import render_to_string

        templates = [render_to_string(get_template_for_object(object), {'object':object, 
                                                                        'content_type':ContentType.objects.get_for_model(object.__class__).id,
                                                                        'target_id':target_id,
                                                                        'data_id':data_id,
                                                                        'STATIC_URL':getattr(project_settings, 'STATIC_URL', ''), 
                                                                        'MEDIA_URL':getattr(project_settings, 'MEDIA_URL', '')}) for object in objects]
        return "\n".join(templates)
    
    def get_initial_data(self, objects):
        return ",".join([encode_relatedcontent_data(object) for object in objects])
    
class RelatedContentField(Field):
    """
    Form field respresenting a target area for rendering selected objects, a hidden input for 
    holding the current set of selected objects and a link for initiating the thickbox
    iframe which contains the selection change_list.  Used for none ajax modes of operation for
    django_relatecontent selection.
    """
    
    widget = RelatedContentWidget
    
    def __init__(self, base_content_type = None, object_id = None, usage = None, iframe_width = 600, iframe_height = 450, *args, **kwargs):
        self.base_content_type = base_content_type
        self.object_id = object_id
        self.iframe_width, self.iframe_height = iframe_width, iframe_height
        self.base_content_type_object = ContentType.objects.get(id = int(base_content_type))
        if not self.object_id == -1:
            self.object = self.base_content_type_object.model_class().objects.get(id = self.object_id)
        else:
            self.object = None
        self.usage = usage
        self.initial_data = self.get_initial_data()
        super(RelatedContentField, self).__init__(*args, **kwargs)
    
    def widget_attrs(self, widget):
        attrs = {}
        attrs['base_id'] = "%s_%s" % (str(self.base_content_type), str(self.object_id))
        attrs['base_url'] = reverse('django-relatedcontent-select', args=[self.base_content_type, self.object_id, self.usage])
        attrs['iframe_width'] = self.iframe_width
        attrs['iframe_height'] = self.iframe_height
        attrs['initial_data'] = self.initial_data
        attrs['base_object'] = self.object
        attrs['base_content_type'] = self.base_content_type
        attrs['base_object_id'] = self.object_id
        return attrs 
    
    def get_initial_data(self):
        if self.object:
            current_associations = ContentAssociation.objects.associations_for_object(self.object, self.usage)
            current_objects = [x.child for x in current_associations]
        else:
            current_objects = []
        return current_objects
    
    def get_internal_type(self):
        return "RelatedContentField"