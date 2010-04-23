import datetime

import django.http as http
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.http import Http404

def main(request):
    return shortcuts.render_to_response('core/main.html',
                                        {},
                                        context_instance = RequestContext(request))
    
def contribute(request):
    return shortcuts.render_to_response('core/contribute.html',
                                        {},
                                        context_instance = RequestContext(request))
def init(request):
    from core.init import init_database
    init_database()
    return shortcuts.render_to_response('core/contribute.html',
                                        {},
                                        context_instance = RequestContext(request))
            