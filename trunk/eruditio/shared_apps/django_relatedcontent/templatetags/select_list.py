from django import template
from django.template import Node, NodeList, Template, Context, Variable, VariableDoesNotExist
from django.template.defaulttags import IfEqualNode
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist

from django_relatedcontent.utils import resolve_variable
from django.contrib.admin.templatetags.admin_list import result_headers, items_for_result

register = template.Library()

def results(cl):
    for res in cl.result_list:
        if res.id in cl.related_objects:
            res.already_related = True
        else:
            res.already_related = False
        yield (res, list(items_for_result(cl, res, None)))

def result_list(cl):
    return {'cl': cl,
            'result_headers': list(result_headers(cl)),
            'results': list(results(cl))}

@register.tag(name="select_result_list")
def do_select_result_list(parser, token):
    try:
        tag, cl, mode  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires one argument" % token.contents.split()[0]
    return SelectResultList(cl, mode)

class SelectResultList(template.Node):
    def __init__(self, cl, mode):
        self.cl = cl
        self.mode = mode
        
    def render(self,  context):
        cl = resolve_variable(self.cl, context, self.cl)
        mode = resolve_variable(self.mode, context, self.mode)
        
        results_context = result_list(cl)
        if mode == 'form/js':
            results_context['ajax'] = False
        else:
            results_context['ajax'] = True
        return render_to_string("django_relatedcontent/select_change_list_results.html", results_context, context)