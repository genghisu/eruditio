"""
Helper templatetags for getting Badge related data into the templates.
"""

from django import template
from django.template import Node, NodeList, Template, Context, Variable, VariableDoesNotExist
from django.template.defaulttags import IfEqualNode
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.loader import render_to_string

from django_utils.templatetag_helpers import resolve_variable, copy_context
from django_badges.models import BadgeInstance, Badge

register = template.Library()

@register.tag(name="associate_badges")
def do_associate_edits(parser,  token):
    """
    Template tag that takes one parameter node which should
    be an user object.
    """
    try:
        tag, node  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires one argument" % token.contents.split()[0]
    return AssociateBadges(node)

class AssociateBadges(template.Node):
    """
    Associates the number of each level of Badge object (Gold, Silver and Bronze)
    with the target user (node) by modifying the current template context.
    """
    def __init__(self, node):
        self.node = node
        
    def render(self,  context):
        node = resolve_variable(self.node, context, self.node)
        badges = Badge.objects.badges_for_user(node)
        node.gold_badges = badges.filter(badge__level = 'Gold').count()
        node.silver_badges = badges.filter(badge__level = 'Silver').count()
        node.bronze_badges = badges.filter(badge__level = 'Bronze').count()
        node.badges = badges
        return ''