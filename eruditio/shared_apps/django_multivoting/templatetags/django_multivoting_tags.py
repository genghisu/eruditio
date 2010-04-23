from django import template
from django.template import Node, NodeList, Template, Context, Variable, VariableDoesNotExist
from django.template.defaulttags import IfEqualNode
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.template.context import Context

from django_utils.templatetag_helpers import resolve_variable
from django_multivoting.models import Vote

register = template.Library()

@register.tag(name="popularity")
def do_get_popularity(parser,  token):
    """
    ModelPopularity
    @object - object to return the popularity for
    """
    try:
        tag, object  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires one argument" % token.contents.split()[0]
    return ModelPopularity(object)

class ModelPopularity(template.Node):
    """
    TODO
    """
    
    def __init__(self, object):
        self.object = object
        
    def render(self,  context):
        object = resolve_variable(self.object, context, self.object)
        popularity = Vote.objects.popularity(object)
        return popularity.popularity

@register.tag(name="associate_popularity")
def do_associate_popularity(parser, token):
    """
    AssociatePopularity
    @object - object to return the popularity for
    """
    try:
        tag, object  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires one argument" % token.contents.split()[0]
    return AssociatePopularity(object)

class AssociatePopularity(template.Node):
    """
    """
    
    def __init__(self, object):
        self.object = object
    
    def render(self, context):
        object = resolve_variable(self.object, context, self.object)
        object.popularity = Vote.objects.popularity(object).popularity
        context[self.object] = object
        return ''
        