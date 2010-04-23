import urllib

from django import template
from django.template import Node, NodeList, Template, Context, Variable, VariableDoesNotExist
from django.template.defaulttags import IfEqualNode
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from django_utils.templatetag_helpers import resolve_variable, copy_context
import tagging.models
from tagging.models import Tag, TaggedItem

register = template.Library()
    
@register.tag(name="tagged_content_row")
def do_tagged_content_row(parser, token):
    try:
        tag, content, template = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires two arguments" % token.contents.split()[0]
    return TaggedContentRow(content, template)

class TaggedContentRow(template.Node):
    """
    @content
    """
    def __init__(self, content, template):
        self.content = content
        self.template = template
        
    def render(self, context):
        content = resolve_variable(self.content, context, None)
        template = resolve_variable(self.template, context, self.template)
        new_context = copy_context(context)
        
        if content.__class__ == TaggedItem:
            content_type_object = ContentType.objects.get_for_model(content.object.__class__)
            new_context['node'] = content.object
            new_context['node_content_type'] = content_type_object.id
            new_context['model'] = content_type_object.model
        else:
            content_type_object = ContentType.objects.get_for_model(content.__class__)
            new_context['node'] = content
            new_context['node_content_type'] = content_type_object.id
            new_context['model'] = content_type_object.model
        
        context['view_url'] = reverse('content-redirect-by-id', args=[new_context['node_content_type'],
                                                                      new_context['node'].id])
        return render_to_string(template, {}, context)

@register.tag(name="associated_tags") 
def do_associated_tags(parser, token):
    """
    AssociatedTags
    """
    try:
        tag, tag_name, content_type = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires one argument" % token.contents.split()[0]
    return AssociatedTags(tag_name, content_type)

class AssociatedTags(template.Node):
    """
    Renders a list of tags associated with the target tag.
    """
    def __init__(self, tag, content_type):
        self.tag = tag
        self.content_type = content_type
    
    def render(self, context):
        tag = urllib.unquote(resolve_variable(self.tag, context, self.tag))
        content_type = resolve_variable(self.content_type, context, self.content_type)
        
        if not str(content_type).strip():
            associated_tags = Tag.meta_objects.related_for_tags(tag, counts=True, min_count=50)[0:15]
            context['node_content_type'] = -1
        else:
            content_type_object = ContentType.objects.get(id=int(content_type))
            model_object = content_type_object.model_class()
            associated_tags = Tag.objects.related_for_model(tag, model_object, counts=True)
            context['node_content_type'] = content_type_object.id
            
        context['tags'] = associated_tags
        return render_to_string('django_metatagging/associated_tags.html', {}, context)

@register.tag(name="associated_tags_for_object")
def do_associated_tags_for_object(parser, token):
    """
    AssociatedTags
    """
    try:
        tag, object = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires one argument" % token.contents.split()[0]
    return AssociatedTagsForObject(object)

class AssociatedTagsForObject(template.Node):
    """
    Renders a list of tags associated with the target object.
    """
    def __init__(self, object):
        self.object = object
    
    def render(self, context):
        object = resolve_variable(self.object, context, self.object)
        tags = [tag.name for tag in Tag.objects.get_for_object(object)]
        
        content_type_object = ContentType.objects.get_for_model(object.__class__)
        model_object = object.__class__
        associated_tags = Tag.objects.related_for_model(tags, model_object, counts=True)
        context['node_content_type'] = content_type_object.id
        context['tags'] = associated_tags
        return render_to_string('django_metatagging/associated_tags.html', {}, context)

@register.tag(name="related_objects")
def do_related_objects(parser, token):
    """
    AssociatedTags
    """
    try:
        tag, object = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires one argument" % token.contents.split()[0]
    return RelatedObjects(object)

class RelatedObjects(template.Node):
    """
    Renders a list of tags associated with the target object.
    """
    def __init__(self, object):
        self.object = object
    
    def render(self, context):
        object = resolve_variable(self.object, context, self.object)
        
        content_type_object = ContentType.objects.get_for_model(object.__class__)
        model_object = object.__class__
        related_objects = TaggedItem.objects.get_related(object, model_object, num=10)
        context['node_content_type'] = content_type_object.id
        context['related_objects'] = related_objects
        return render_to_string('django_metatagging/related_objects.html', {}, context)
    
@register.tag(name='active_tags')
def do_most_active_tags(parser, token):
    try:
        tag, content_type, _as, context_variable = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires three arguments" % token.contents.split()[0]
    return ActiveTags(content_type, context_variable)

class ActiveTags(template.Node):
    """
    @tag_name
    @content_type
    """
    def __init__(self, content_type, context_variable):
        self.content_type = content_type
        self.context_variable = context_variable
    
    def render(self, context):
        content_type = resolve_variable(self.content_type, context, self.content_type)
        
        try:
            content_type_object = ContentType.objects.get(id=int(content_type))
        except ValueError:
            content_type_object = None
        except ObjectDoesNotExist:
            content_type_object = None
            
        if content_type_object:
            most_active_tags = tagging.models.Tag.meta_objects.most_active(content_type_object.id, 5)
        else:
            most_active_tags = []
        
        context[self.context_variable] = most_active_tags
        return ''

@register.tag(name="cloud_for_model") 
def do_tag_cloud(parser, token):
    """
    TagCloud
    """
    try:
        tag, content_type = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires one argument" % token.contents.split()[0]
    return CloudForModel(content_type)

class CloudForModel(template.Node):
    """
    Renders a tag cloud for the target model.
    """
    def __init__(self, content_type):
        self.content_type = content_type
    
    def render(self, context):
        content_type = resolve_variable(self.content_type, context, self.content_type)
        new_context = copy_context(context)
        content_type_object = ContentType.objects.get(id=int(content_type))
        model_object = content_type_object.model_class()
        tag_cloud = Tag.objects.cloud_for_model(model_object, steps=1, min_count=25)[0:50]
        new_context['node_content_type'] = content_type_object.id
        new_context['tags'] = tag_cloud
        
        return render_to_string('django_metatagging/cloud_for_model.html', {}, context)
