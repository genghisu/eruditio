from django import template
from django.template import Node, NodeList, Template, Context, Variable, VariableDoesNotExist
from django.template.defaulttags import IfEqualNode
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.loader import render_to_string

from django_utils.templatetag_helpers import resolve_variable, copy_context
from django_contenthistory.models import ModelHistory

register = template.Library()

@register.tag(name="associate_latest_edit")
def do_associate_latest_edit(parser,  token):
    """
    AssociateLatestEdit
    """
    try:
        tag, node  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires one argument" % token.contents.split()[0]
    return AssociateLatestEdit(node)

class AssociateLatestEdit(template.Node):
    """
    Associate the latest edit with the target object as object.edit.
    """
    def __init__(self, node):
        self.node = node
        
    def render(self,  context):
        node = resolve_variable(self.node, context, self.node)
        edits = ModelHistory.objects.edits_for_object(node)
        try:
            node.edit = edits[0]
        except IndexError:
            node.edit = None
        return ''