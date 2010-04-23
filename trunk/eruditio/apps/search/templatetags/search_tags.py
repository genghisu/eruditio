from django import template
from django.template import Node, NodeList, Template, Context, Variable, VariableDoesNotExist
from django.template.defaulttags import IfEqualNode
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from django_utils.templatetag_helpers import resolve_variable, copy_context

register = template.Library()
    
@register.tag(name="search_row")
def do_search_row(parser,  token):
    try:
        tag, result, template = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires two arguments" % token.contents.split()[0]
    return SearchRow(result, template)

class SearchRow(template.Node):
    """
    @content
    """
    def __init__(self,  result, template):
        self.result = result
        self.template = template
        
    def render(self,  context):
        result = resolve_variable(self.result,  context,  self.result)
        content = result.object
        template = resolve_variable(self.template, context, self.template)
        new_context = copy_context(context)
        
        content_type_object = ContentType.objects.get_for_model(content.__class__)
        new_context['node'] = content
        new_context['node_content_type'] = content_type_object.id
        new_context['model'] = content_type_object.model
        
        context['view_url'] = reverse('content-redirect-by-id', args=[new_context['node_content_type'],
                                                                      new_context['node'].id])
        return render_to_string(template,  {},  context)