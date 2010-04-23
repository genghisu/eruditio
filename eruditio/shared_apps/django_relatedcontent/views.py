import django.http as http
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, NoReverseMatch

import django_relatedcontent.config as settings
from django_relatedcontent.models import ContentUsage, ContentAssociation
from django_relatedcontent.utils import SelectChangeList, persist_get_parameters, get_template_for_object

def select_main(request, base_content_type, base_object_id, usage):
    """
    Main view for delegating content selection process.  Will attempt to render a template
    with all the possible child content types based on AvailableContentUsages in the database.
    """
    available_usages = ContentUsage.objects.usage_for_base_content_type(base_content_type, usage)
    
    base_handler = request.GET.get('select_handler', 'django-relatedcontent-content-select')
    
    for current_usage in available_usages:
        try:
            handler = reverse(base_handler, args=[current_usage.base_model.id, base_object_id, current_usage.selectable_model.id, usage])
            handler = persist_get_parameters(handler, request.GET)
            current_usage.handler = handler
        except NoReverseMatch:
            error = getattr(settings, 'INVALID_HANDLER', 0)
            usage.handler = reverse('django-relatedcontent-error', args=[error])
            
    return shortcuts.render_to_response(
        'django_relatedcontent/select.html', 
        {'available_usages':available_usages, 
         'base_object_id':base_object_id, 
         'target_usage':usage}, 
        context_instance = RequestContext(request),
    )

class Select(object):
    """
    Class with callable instances that render a modified change_list view which
    enables selection of related child objects by creating associations with 
    a base object.
    """
    def __init__(self, change_list_class):
        self.change_list_class = change_list_class
        
    def __call__(self, request, base_content_type, base_object_id, selectable_content_type, usage):
        base_content_type_object = ContentType.objects.get(id = base_content_type)
        base_model = base_content_type_object.model_class()
        selectable_content_type_object = ContentType.objects.get(id = selectable_content_type)
        selectable_model = selectable_content_type_object.model_class()
        
        change_list = self.change_list_class(base_model, base_object_id, selectable_model, usage, request)
        base_context = change_list.context()
        base_context['base_content_type'] = base_content_type
        base_context['selectable_content_type'] = selectable_content_type
        base_context['base_object_id'] = base_object_id
        base_context['usage'] = usage
        base_context['ajax_render_url'] = reverse('django-relatedcontent-render-item')
        
        return shortcuts.render_to_response(settings.DEFAULT_CHANGE_LIST_TEMPLATE, 
                                  base_context, 
                                  context_instance = RequestContext(request))
select_change_list = Select(SelectChangeList)

def select_error(request, error):
    """
    Selection error view.
    """
    return shortcuts.render_to_response('django_relatedcontent/error.html', 
                                  {}, 
                                  context_instance = RequestContext(request))
    
def modify_content_association(request):
    """
    Based on the query parameter add, attempt to add or remove a ContentAssociation
    based on additional query parameters.
    """
    base_content_type = request.GET.get('base_content_type', None)
    base_object_id = request.GET.get('base_object_id', None)
    selectable_content_type = request.GET.get('selectable_content_type', None)
    selectable_object_id = request.GET.get('selectable_object_id', None)
    usage = request.GET.get('usage', None)
    add = request.GET.get('add', None)
    
    base_content_type_object = ContentType.objects.get(id = int(base_content_type))
    selectable_content_type_object = ContentType.objects.get(id = int(selectable_content_type))
    
    try:
        usage_object = ContentUsage.objects.get(name = usage)
    except ObjectDoesNotExist:
        usage_object = None
        
    if add == 'true':
        association = ContentAssociation.objects.add_association(base_content_type_object, base_object_id, selectable_content_type_object, selectable_object_id, usage_object)
    elif add == 'false':
        association = ContentAssociation.objects.remove_association(base_content_type_object, base_object_id, selectable_content_type_object, selectable_object_id, usage_object)
        
    return shortcuts.render_to_response('django_relatedcontent/modify_content_association.html',
                                        {'association':association})
    
def render_content_item(request):
    """
    Renders a content item based on get_template_for_object to generate css and javascript
    associated with a child object that has been selected to be associated.
    """
    from django.template.loader import get_template, render_to_string
    
    base_content_type = request.GET.get('base_content_type', None)
    base_object_id = request.GET.get('base_object_id', None)
    selectable_content_type = request.GET.get('selectable_content_type', None)
    selectable_object_id = request.GET.get('selectable_object_id', None)
    style = request.GET.get('style', None)
    target_id = request.GET.get('target_id', None)
    data_id = request.GET.get('data_id', None)
    usage = request.GET.get('usage', None)
    
    selectable_content_type_object = ContentType.objects.get(id = selectable_content_type)
    selectable_object = selectable_content_type_object.model_class().objects.get(id = selectable_object_id)
    
    target_template = get_template_for_object(selectable_object, style)
    return shortcuts.render_to_response(target_template, 
                                        {'selectable_object':selectable_object,
                                         'selectable_content_type':selectable_content_type_object.id,
                                         'base_object_id':base_object_id,
                                         'base_content_type':base_content_type,
                                         'target_id':target_id,
                                         'usage':usage,
                                         'data_id':data_id}, 
                                        context_instance = RequestContext(request))
