import django.http as http
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

import django_multivoting.config as config
import django_multivoting.models as models

def vote(request,  content_type,  object_id,  vote_mode = None, template_mode = 'standard', template = 'standard_vote.html'):
    model_content_type = ContentType.objects.get(id = content_type)
    target_model = model_content_type.model_class()
    node = target_model.objects.get(id = object_id)
    confirmation = models.Vote.objects.handle_vote(request.user, node, vote_mode)
    template_name = 'django_multivoting/%s' % (template)
    
    return shortcuts.render_to_response(
            template_name, 
            {'node':node, 'confirmation':confirmation,  'node_content_type':content_type,  'object_id':object_id,  
             'model':model_content_type.model,
             'vote_mode':vote_mode, 'vote_class':template_mode}, 
            context_instance = RequestContext(request), 
    )
