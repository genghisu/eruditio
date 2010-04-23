from django.contrib.contenttypes.models import ContentType
from django_utils.render_helpers import render_or_default
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.contrib.contenttypes.models import ContentType
import django.http as http

from django_moderation.models import ContentApprovalVote
from django_community.decorators import UserRequired, user_required
from django_community_wiki.community_wiki import community_wiki

@user_required
def queue(request, content_type = None):
    """
    View that generates a context containing an object that the
    logged in user can moderate or None, if there are no
    available objects to moderate.
    """
    def get_template_for_object(object):
        from django.template.loader import get_template
        from django.template import TemplateDoesNotExist
    
        content_type_object = ContentType.objects.get_for_model(object.__class__)
        style_template = "django_moderation/%s/%s.html" % (content_type_object.app_label, content_type_object.model)
    
        try:
            get_template(style_template)
            target_template = style_template
        except TemplateDoesNotExist, e:
            target_template = "django_moderation/base_queue_item.html"
        return target_template
    
    user = request.user
    instance = ContentApprovalVote.objects.queue(user)
    if instance:
        model = instance.content_type.model_class()
        node = model.objects.get_all(id = instance.object_id)
        node.model = node.__class__.__name__
        node.template = get_template_for_object(node)
        node_content_type = instance.content_type.id
        content_type_object = instance.content_type
        node.accepts = ContentApprovalVote.objects.filter(content_type = content_type_object,
                                                          object_id = node.id,
                                                          mode = 'accept').count()                    
        node.rejects = ContentApprovalVote.objects.filter(content_type = content_type_object,
                                                          object_id = node.id,
                                                          mode = 'reject').count()
    else:
        node = None
        node_content_type = None
    
    return shortcuts.render_to_response(
                'django_moderation/queue.html',
                {'node':node,
                 'node_content_type':node_content_type},
                context_instance = RequestContext(request)
    )

def moderate(request, content_type, object_id, mode):
    """
    Cast an accept, pass or reject vote to moderate an object.
    """
    user = request.user
    content_type_object = ContentType.objects.get(id = content_type)
    object = content_type_object.model_class().objects.get_all(id = object_id)
    status = ContentApprovalVote.objects.vote(object, user, mode)
    
    redirect_url = request.GET.get('queue_url', reverse('moderation-queue'))
    return http.HttpResponseRedirect(redirect_url)

def delete(request, content_type, object_id):
    """
    Cast an accept, pass or reject vote to moderate an object.
    """
    user = request.user
    content_type_object = ContentType.objects.get(id = content_type)
    node = content_type_object.model_class().objects.get(id = object_id)
    community_wiki.delete_content(node)
    
    redirect_url = reverse('content-list-redirect', args=[content_type_object.id])
    return http.HttpResponseRedirect(redirect_url)

class FlagAction(object):
    """
    Class with callable instances that provide flagging functionality for any
    content type.
    """
    def __init__(self, model, form_builder, template = None, redirect_url = None):
        self.model = model
        self.form_builder = form_builder
        self.template = template
        self.redirect_url = redirect_url
        self.content_type = ContentType.objects.get_for_model(model)
    
    def __call__(self, request, object_id):
        """
        Provides a context with the object being flagged, the existing flags
        on that object, an instance of a FlagForm.  Renders the template
        provided in self.template.
        """
        from django_moderation.models import ContentFlag, ContentFlagVote
        
        remove = request.GET.get('remove', False)
        FlagForm = self.form_builder()
        object = get_object_or_404(self.model, id = object_id)
        
        if request.POST or remove:
            if remove:
                existing_flag = ContentFlagVote.objects.get_vote_for_content(object, request.user)
                if existing_flag:
                    existing_flag.delete()
                    return http.HttpResponseRedirect(reverse(self.redirect_url, args=[object.id]))
            else:
                form = FlagForm(request.POST, request.FILES)
                if form.is_valid():
                    ContentFlagVote.objects.add_vote(self.content_type.id,
                                                     object_id,
                                                     form.cleaned_data['action'], 
                                                     form.cleaned_data['reason'], 
                                                     form.cleaned_data['details'],
                                                     request.user)
                    return http.HttpResponseRedirect(reverse(self.redirect_url, args=[object.id]))
        else:
            form = FlagForm()
            
        existing_flag = ContentFlagVote.objects.get_vote_for_content(object, request.user)
        return shortcuts.render_to_response(
                self.template,
                {'form':form, 
                 'object_id':object.id, 
                 'node':object, 
                 'existing_flag':existing_flag},
                context_instance = RequestContext(request)
        )