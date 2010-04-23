import datetime

import django.http as http
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.http import Http404

from haystack.forms import SearchForm
import django_utils.pagination as pagination
from django_utils import request_helpers

def search(request, load_all=True, form_class=SearchForm, searchqueryset=None, context_class=RequestContext, extra_context=None):
    page = request_helpers.get_page(request)
    query = ''
    results = []
    
    if request.GET:
        form = form_class(request.GET, searchqueryset=searchqueryset, load_all=load_all)
        
        if form.is_valid():
            query = form.cleaned_data['q']
            results = form.search()
            current_page, page_range = pagination.paginate_queryset(results, 30, 5, page)
    else:
        current_page, page_range = None, None
        
    context = {
        'current_page':current_page,  
        'page_range':page_range,
        'query': query,
    }
    
    return shortcuts.render_to_response('search/search.html', 
                                        context, 
                                        context_instance=context_class(request))