from django import template
from django.template import Node, NodeList, Template, Context, Variable, VariableDoesNotExist
from django.template.defaulttags import IfEqualNode
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.loader import render_to_string

from django_utils.templatetag_helpers import resolve_variable, copy_context
import django_comments.forms as forms
import django_comments.models as models

register = template.Library()

@register.tag(name="comments")
def render_comments(parser,  token):
    """
    Template tag taking these params:
    
    @param content_type - C{int} corresponding to object content type id
    @param model_name - C{str} of name of target model
    @param node_id - C{int} id of object
    @param comment_class - C{str} of comment rendering format
    """
    try:
        tag,  content_type, model_name, node_id, comment_class = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires two arguments" % token.contents.split()[0]
    return Comments(content_type, model_name, node_id, comment_class)

class Comments(template.Node):
    """
    Renders a list of comments for a target parent object.
    """
    def __init__(self, content_type, model_name, node_id, comment_class, count = 5):
        self.content_type = content_type
        self.model_name = model_name
        self.node_id = node_id
        self.comment_class = comment_class
        self.count = count
        
    def render(self,  context):
        context = copy_context(context)
        content_type = resolve_variable(self.content_type, context, self.content_type)
        model_name = resolve_variable(self.model_name,  context, self.model_name)
        node_id = resolve_variable(self.node_id,  context, self.node_id)
        comment_class = resolve_variable(self.comment_class, context, self.comment_class)
        
        content_type_object = ContentType.objects.get(id = content_type)
        node = content_type_object.model_class().objects.get(id = node_id)
        all_comments = models.Comment.objects.comments_for_object(node, 'highest_rated')
        additional_count = all_comments.count() - self.count
        CommentForm = forms.build_comment_form(comment_class)
        comment_form = CommentForm()
        
        template = render_to_string('django_comments/standard_comments.html',   
                                        {'comment_target_node':node,
                                         'comments':all_comments[0:self.count],
                                         'comment_target_content_type':content_type_object.id,
                                         'comment_target_model':model_name,
                                         'comment_form':comment_form,
                                         'comment_class':comment_class,
                                         'additional_count':additional_count},  
                                         context
                                        )
        return template

@register.tag(name="comments_count")
def do_get_comments_count(parser,  token):
    """
    Template tag taking these params:
    
    @object - object to return the comment count for
    """
    try:
        tag, object  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires one argument" % token.contents.split()[0]
    return ModelComments(object)

class ModelComments(template.Node):
    """
    Returns the number of comments associated with a given object.
    """
    
    def __init__(self, object):
        self.object = object
        
    def render(self,  context):
        object = resolve_variable(self.object, context, self.object)
        comments = models.Comment.objects.comments_for_object(object)
        object.comments_count = comments.count()
        return object.comments_count