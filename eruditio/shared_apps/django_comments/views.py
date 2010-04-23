"""
Views for submitting and editing comments.
"""

import django.http as http
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse

import django_comments.models as models
import django_comments.forms as forms
from django_utils import request_helpers

def ajax_comment(request,  content_type,  object_id, comment_class = 'standard', parent = None):
    """
    Handles ajax submission of comments.
    
    Attempts to render django_comments/standard_comment_list.html after
    the comment has been added.
    
    @param comment_class - used in template for layout and css purposes.
    @param parent - parent comment.
    @param content_type - content type of object which comment belongs to.
    @param object_id - id of parent object.
    """
    user = request.user
    
    CommentForm = forms.build_comment_form(comment_class)
    
    if user and request.POST:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data.get('comment', '')
            target_model = ContentType.objects.get(id = content_type)
            target_object = target_model.model_class().objects.get(id = object_id)
            models.Comment.objects.add_comment(user, target_object, comment, parent)    
                 
    return shortcuts.render_to_response(
            'django_comments/standard_comment_list.html', 
            {'node':target_object, 
             'node_content_type':content_type,  
             'object_id':object_id,  
             'comments':models.Comment.objects.comments_for_object(target_object),  
             'comment_class':comment_class}, 
            context_instance = RequestContext(request), 
    )

def edit_comment(request,  comment_id):
    """
    Handles the editing of comments.
    
    Uses django_comments.forms.build_edit_comment_form to generate
    the edit form.
    
    @param comment_id - id of comment to edit.
    """
    user = community_helpers.get_logged_user(request)
    
    if user:
        comment = models.Comment.objects.get(id = comment_id)
        EditCommentForm = forms.build_edit_comment_form(comment)
        if request.POST:
            form = EditCommentForm(request.POST,  request.FILES)
            if form.is_valid():
                form.handle_edit(user, comment)
                return http.HttpResponseRedirect(reverse('content-redirect-by-id',  args=[comment.content_type.id,  comment.object_id]))
        else:
            form = EditCommentForm()
    return shortcuts.render_to_response(
        'comments/edit_comment.html', 
        {'form':form,  'comment':comment,  'node_content_type':comment.content_type.id,  'node_object_id':comment.object_id}, 
        context_instance = RequestContext(request)
    )

def list(request, content_type, object_id, comment_class = 'standard'):
    """
    Renders a list of comments associated with a target object.
    
    @param content_type - content type of object which comment belongs to.
    @param object_id - id of parent object.
    @param comment_class - used in template for layout and css purposes.
    """
    option = request_helpers.get_sort(request, 'most_recent')
    content_type_object = ContentType.objects.get(id = content_type)
    node = content_type_object.model_class().objects.get(id = object_id)
    all_comments = models.Comment.objects.comments_for_object(node)
    model_name = content_type_object.model
    
    return shortcuts.render_to_response('django_comments/standard_comment_list.html',   
                                            {'comment_target_node':node,
                                             'comments':all_comments,
                                             'comment_target_model':model_name,
                                             'comment_class':comment_class},  
                                             context_instance = RequestContext(request)
                                        )