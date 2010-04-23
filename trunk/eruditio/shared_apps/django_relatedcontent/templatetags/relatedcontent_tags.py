from django import template
from django.template import Node, NodeList, Template, Context, Variable, VariableDoesNotExist
from django.template.defaulttags import IfEqualNode
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.template.context import Context
from django.core.urlresolvers import reverse

from django_relatedcontent.utils import (generate_enable_thickbox, generate_relatedcontent_url, generate_thickbox_url,
                                        encode_relatedcontent_data, get_template_for_object, generate_bind_close_for_target,
                                        generate_target_id, generate_data_id, generate_init_id, resolve_variable,
                                        render_initial_target)

register = template.Library()

@register.tag(name="enable_thickbox")
def do_enable_thickbox(parser,  token):
    """
    Initiates thickbox based on the information provided by the target link.
    """
    try:
        tag, link_id  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires one argument" % token.contents.split()[0]
    return EnableThickbox(link_id)

class EnableThickbox(template.Node):
    """
    Initiates thickbox based on the information provided by the target link.
    """
    
    def __init__(self, link_id):
        self.link_id = link_id
        
    def render(self,  context):
        link_id = resolve_variable(self.link_id, context, self.link_id)
        
        return generate_enable_thickbox(link_id)
    
@register.tag(name='update_target')
def do_update_target(parser,  token):
    """
    UpdateTarget
    """
    try:
        tag, link_id, target_id, data_id, ajax_url, base_content_type, base_object_id, selectable_content_type, selectable_object_id, usage  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires one argument" % token.contents.split()[0]
    return UpdateTarget(link_id, target_id, data_id, ajax_url, base_content_type, base_object_id, selectable_content_type, selectable_object_id, usage)

class UpdateTarget(template.Node):
    """
    Attach on click event to a link which updates the selection area with the current child object
    associated with the link.  Updates the target area by calling the ajax url which will
    return the associated template.
    """
    
    def __init__(self, link_id, target_id, data_id, ajax_url, base_content_type, base_object_id, selectable_content_type, selectable_object_id, usage):
        self.link_id = link_id
        self.target_id = target_id
        self.ajax_url = ajax_url
        self.data_id = data_id
        self.base_content_type = base_content_type
        self.selectable_content_type = selectable_content_type
        self.base_object_id = base_object_id
        self.selectable_object_id = selectable_object_id
        self.usage = usage
        
    def render(self,  context):
        values = {}
        link_id = values['link_id'] = resolve_variable(self.link_id, context, self.link_id)
        target_id = values['target_id'] = resolve_variable(self.target_id, context, self.target_id)
        ajax_url = values['ajax_url'] = resolve_variable(self.ajax_url, context, self.ajax_url)
        base_content_type = values['base_content_type'] = resolve_variable(self.base_content_type, context, self.base_content_type)
        selectable_content_type = values['selectable_content_type'] = resolve_variable(self.selectable_content_type, context, self.selectable_content_type)
        base_object_id = values['base_object_id'] = resolve_variable(self.base_object_id, context, self.base_object_id)
        selectable_object_id = values['selectable_object_id'] = resolve_variable(self.selectable_object_id, context, self.selectable_object_id)
        data_id = values['data_id'] = resolve_variable(self.data_id, context, self.data_id)
        usage = values['usage'] = resolve_variable(self.usage, context, self.usage)
        
        script = """<script type='text/javascript'>$("#%(link_id)s").bind("click", 
                        function(e) {$.update_target_call("%(target_id)s", "%(data_id)s", "%(ajax_url)s", 
                                        "%(base_content_type)s", "%(base_object_id)s",
                                        "%(selectable_content_type)s", "%(selectable_object_id)s", "%(usage)s"); 
                    return false;});</script>""" % \
                values
        return "\n" + script + "\n"
    
@register.tag(name="update_data")
def do_update_data(parser, token):
    """
    UpdateData
    """
    try:
        tag, link_id, data_id, content_type, object_id  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires one argument" % token.contents.split()[0]
    return UpdateData(link_id, data_id, content_type, object_id)

class UpdateData(template.Node):
    """
    Attach on click event to a link which updates the hidden input with the associated child data. 
    """
    
    def __init__(self, link_id, data_id, content_type, object_id):
        self.link_id = link_id
        self.data_id = data_id
        self.content_type = content_type
        self.object_id = object_id
        
    def render(self,  context):
        link_id = resolve_variable(self.link_id, context, self.link_id)
        data_id = resolve_variable(self.data_id, context, self.data_id)
        content_type = resolve_variable(self.content_type, context, self.content_type)
        object_id = resolve_variable(self.object_id, context, self.object_id)
        
        script = """<script type='text/javascript'>$("#%s").bind("click", function() {$.update_data_call("%s", "%s", "%s"); return false;});</script>""" % \
                (link_id, data_id, content_type, object_id)
        return "\n" + script + "\n"

@register.tag(name="disable_update")
def do_update_data(parser, token):
    """
    DisableUpdate
    """
    try:
        tag, link_id, row_id  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires two argument" % token.contents.split()[0]
    return DisableUpdate(link_id, row_id)

class DisableUpdate(template.Node):
    """
    Remove all events associated with the target link and causes the dom element with
    id = row_id to fade to 30% opacity.
    """
    
    def __init__(self, link_id, row_id):
        self.link_id = link_id
        self.row_id = row_id
        
    def render(self,  context):
        link_id = resolve_variable(self.link_id, context, self.link_id)
        row_id = resolve_variable(self.row_id, context, self.row_id)
        
        script = """<script type='text/javascript'>$("#%s").bind("click", function() {$.disable_update("%s", "%s"); return false;});</script>""" % \
                (link_id, link_id, row_id)
        return "\n" + script + "\n"
    
@register.tag(name="check_related_item")
def do_check_related_item(parser, token):
    """
    CheckRelatedItem
    """
    try:
        tag, data_id, content_type, object_id, row_id, link_id = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires two argument" % token.contents.split()[0]
    return CheckRelatedItem(data_id, content_type, object_id, row_id, link_id)

class CheckRelatedItem(template.Node):
    """
    Checks an object to determine if it has already been associated with the base object.
    If so, fade that child object row to opacity = 30%.
    """
    def __init__(self, data_id, content_type, object_id, row_id, link_id):
        self.data_id = data_id
        self.content_type = content_type
        self.object_id = object_id
        self.row_id = row_id
        self.link_id = link_id
        
    def render(self,  context):
        data_id = resolve_variable(self.data_id, context, self.data_id)
        content_type = resolve_variable(self.content_type, context, self.content_type)
        object_id = resolve_variable(self.object_id, context, self.object_id)
        row_id = resolve_variable(self.row_id, context, self.row_id)
        link_id = resolve_variable(self.link_id, context, self.link_id)
        
        script = """<script type='text/javascript'>$.check_related_item("%s", "%s", "%s", "%s", "%s");</script>""" % \
                (data_id, content_type, object_id, row_id, link_id)
        return "\n" + script + "\n"

@register.tag(name="remove_target_item")
def do_remove_target_item(parser, token):
    """
    RemoveTargetItem
    """
    try:
        tag, link_id, data_id, target_id, remove_url, base_content_type, base_object_id, selectable_content_type, selectable_object_id, usage  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires two argument" % token.contents.split()[0]
    return RemoveTargetItem(link_id, data_id, target_id, remove_url, base_content_type, base_object_id, selectable_content_type, selectable_object_id, usage)

class RemoveTargetItem(template.Node):
    """
    Attach on click event to the target link that removes the associated child object
    from the target selection area and modifies the hidden input data to reflect the 
    modification.  Used for form/js mode.
    """
    def __init__(self, link_id, data_id, target_id, remove_url, base_content_type, base_object_id, selectable_content_type, selectable_object_id, usage):
        self.data_id = data_id
        self.target_id = target_id
        self.base_content_type = base_content_type
        self.selectable_content_type = selectable_content_type
        self.base_object_id = base_object_id
        self.selectable_object_id = selectable_object_id
        self.usage = usage
        self.link_id = link_id
        self.remove_url = remove_url
        
    def render(self,  context):
        values = {}
        data_id = values['data_id'] = resolve_variable(self.data_id, context, self.data_id)
        target_id = values['target_id'] = resolve_variable(self.target_id, context, self.target_id)
        base_content_type = values['base_content_type'] = resolve_variable(self.base_content_type, context, self.base_content_type)
        selectable_content_type = values['selectable_content_type'] = resolve_variable(self.selectable_content_type, context, self.selectable_content_type)
        base_object_id = values['base_object_id'] = resolve_variable(self.base_object_id, context, self.base_object_id)
        selectable_object_id = values['selectable_object_id'] = resolve_variable(self.selectable_object_id, context, self.selectable_object_id)
        usage = values['usage'] = resolve_variable(self.usage, context, self.usage)
        link_id = values['link_id'] = resolve_variable(self.link_id, context, self.link_id)
        remove_url = values['remove_url'] = resolve_variable(self.remove_url, context, self.remove_url).strip()
        
        script = """<script type='text/javascript'>
                    $("#%(link_id)s").click(function(){
                    $.remove_from_target("%(target_id)s", "%(remove_url)s", "%(base_content_type)s", 
                                        "%(base_object_id)s", "%(selectable_content_type)s", "%(selectable_object_id)s",
                                        "%(usage)s");
                    $.remove_from_data("%(data_id)s", "%(selectable_content_type)s", "%(selectable_object_id)s");
                    return false;});
                    </script>""" % values
        return "\n" + script + "\n"

@register.tag(name="modify_content_association")
def do_modify_content_association(parser, token):
    """
    ModifyContentAssociation
    """
    try:
        tag, link_id, associate_url, base_content_type, base_object_id, selectable_content_type, selectable_object_id, usage, add = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires two argument" % token.contents.split()[0]
    return ModifyContentAssociation(link_id, associate_url, base_content_type, base_object_id, selectable_content_type, selectable_object_id, usage, add)

class ModifyContentAssociation(template.Node):
    """
    Adds an on click event to the target link which adds or removes a ContentAssociation object.
    Used for ajax modes.
    """
    def __init__(self, link_id, associate_url, base_content_type, base_object_id, selectable_content_type, selectable_object_id, usage, add):
        self.link_id = link_id
        self.associate_url = associate_url
        self.base_content_type = base_content_type
        self.base_object_id = base_object_id
        self.selectable_content_type = selectable_content_type
        self.selectable_object_id = selectable_object_id
        self.usage = usage
        self.add = add
        
    def render(self,  context):
        values = {}
        link_id = values['link_id'] = resolve_variable(self.link_id, context, self.link_id)
        associate_url = values['associate_url'] = resolve_variable(self.associate_url, context, self.associate_url)
        base_content_type = values['base_content_type'] = resolve_variable(self.base_content_type, context, self.base_content_type)
        base_object_id = values['base_object_id'] = resolve_variable(self.base_object_id, context, self.base_object_id)
        usage = values['usage'] = resolve_variable(self.usage, context, self.usage)
        selectable_content_type = values['selectable_content_type'] = resolve_variable(self.selectable_content_type, context, self.selectable_content_type)
        selectable_object_id = values['selectable_object_id'] = resolve_variable(self.selectable_object_id, context, self.selectable_object_id)
        add = values['add'] = resolve_variable(self.add, context, self.add)
        
        script = """<script type='text/javascript'>
                    $("#%(link_id)s").click(function(){
                    $.modify_content_association("%(associate_url)s", 
                                                 "%(base_content_type)s", "%(base_object_id)s", 
                                                 "%(selectable_content_type)s", "%(selectable_object_id)s",
                                                 "%(usage)s", "%(add)s");
                    return false;});
                    </script>""" % values
        return "\n" + script + "\n"
    
@register.tag(name="generate_ajax_select")
def do_generate_ajax_select(parser, token):
    """
    GenerateAjaxSelect
    """
    try:
        tag, base_content_type, base_object_id, usage, update_mode, associate_url, iframe_width, iframe_height = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires two argument" % token.contents.split()[0]
    return GenerateAjaxSelect(base_content_type, base_object_id, usage, update_mode, associate_url, iframe_width, iframe_height)

class GenerateAjaxSelect(template.Node):
    """
    Generates a target area and thickbox link used for ajax mode of related content selection.
    """
    def __init__(self, base_content_type, base_object_id, usage, update_mode, associate_url, iframe_width, iframe_height):
        self.base_content_type = base_content_type
        self.base_object_id = base_object_id
        self.usage = usage
        self.update_mode = update_mode
        self.associate_url = associate_url
        self.iframe_height = iframe_height
        self.iframe_width = iframe_width
        
    def render(self,  context):
        base_content_type = resolve_variable(self.base_content_type, context, self.base_content_type)
        base_object_id = resolve_variable(self.base_object_id, context, self.base_object_id)
        usage = resolve_variable(self.usage, context, self.usage)
        update_mode = resolve_variable(self.update_mode, context, self.update_mode)
        associate_url = resolve_variable(self.associate_url, context, self.associate_url)
        iframe_height = resolve_variable(self.iframe_height, context, self.iframe_height)
        iframe_width = resolve_variable(self.iframe_width, context, self.iframe_width)
        resolved_associate_url = reverse(associate_url)
        
        base_content_type_object = ContentType.objects.get(id = int(base_content_type))
        base_content_model = base_content_type_object.model_class()
        if base_object_id > 0:
            base_object = base_content_model.objects.get(id = base_object_id)
        else:
            base_object = None
        
        target_id = generate_target_id(base_content_type, base_object_id)
        data_id = generate_data_id(base_content_type, base_object_id)
        init_id = generate_init_id(base_content_type, base_object_id)
        
        initial_objects = self.get_initial_data(base_object, usage)
        initial_target = render_initial_target(base_object, 
                                               initial_objects, 
                                               target_id, 
                                               data_id, 
                                               associate_url = resolved_associate_url,
                                               usage = usage)
        
        base_url = reverse('django-relatedcontent-select', args=[base_content_type, base_object_id, usage])
        relatedcontent_url = generate_relatedcontent_url(base_url = base_url, 
                                                         mode = update_mode,
                                                         target_id = target_id,
                                                         data_id = data_id,
                                                         ajax_associate_url = associate_url)
        target_url = generate_thickbox_url(relatedcontent_url, iframe_width, iframe_height)
        
        new_context = {}
        new_context['target_id'] = target_id
        new_context['data_id'] = data_id
        new_context['init_id'] = init_id
        new_context['target_url'] = target_url
        new_context['initial_target'] = initial_target
        context['select_link_id'] = init_id
        
        return render_to_string('django_relatedcontent/generate_ajax_select.html', new_context)
    
    def get_initial_data(self, base_object, usage):        
        from django_relatedcontent.models import ContentAssociation
        
        if base_object:
            current_associations = ContentAssociation.objects.associations_for_object(base_object, usage)
            current_objects = [x.child for x in current_associations]
        else:
            current_objects = []
        return current_objects
    
@register.tag(name="generate_target")
def do_generate_target(parser, token):
    pass

@register.tag(name="generate_select_url")
def do_generate_select_url(parser, token):
    pass