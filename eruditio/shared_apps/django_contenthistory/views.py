try:
    import json
except:
    import simplejson as json

import django.http as http
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from django_contenthistory.models import ModelHistory
from django_contenthistory.utils import associate_revision_fields

def history(request, content_type, object_id):
    """
    View for rendering a list of ModelHistory objects associated with the target object.
    Similar to StackOverflow's content history template.
    """
    content_type_object = ContentType.objects.get(id = int(content_type))
    node = content_type_object.model_class().objects.get(id = int(object_id))
    
    revisions = ModelHistory.objects.filter(content_type = content_type_object,
                                            object_id = object_id).order_by('-date_created')
    for revision in revisions:
        revision = associate_revision_fields(revision)
        revision.description = ",".join([k for k, v in json.loads(revision.data).items() if v])
    
    view_url = reverse('content-redirect-by-id', args=[content_type, object_id])
    
    return shortcuts.render_to_response('django_contenthistory/contenthistory.html',
                                        {'revisions':revisions,
                                         'content_type':content_type,
                                         'object_id':object_id,
                                         'view_url':view_url},
                                         context_instance = RequestContext(request))