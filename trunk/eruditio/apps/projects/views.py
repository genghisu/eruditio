import django.http as http
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

import django_community.utils as community_utils
import django_utils.pagination as pagination
import django_utils.request_helpers as request_helpers
import django_community.decorators as community_decorators
from django_reputation.decorators import reputation_required
import projects.forms as forms
import projects.models as models

def projects_list(request, option = 'most_active'):
    page = request_helpers.get_page(request)
    codes = models.Project.objects.all()
    
    current_page, page_range = pagination.paginate_queryset(codes, 20, 5, page)
    
    return shortcuts.render_to_response(
                'projects/list.html', 
                {'current_page':current_page,  
                 'page_range':page_range,  
                 'sort':option}, 
                context_instance = RequestContext(request),
    )
    
def contribute(request):
    from tagging.models import Tag
    from django_metatagging.utils import parse_tag_input_local
    
    if request.POST:
        form = forms.ProjectForm(request.POST,  request.FILES)
        if form.is_valid():
            code = models.Code.objects.contribute_code(form.cleaned_data['title'], 
                                                        form.cleaned_data['description'], 
                                                        form.cleaned_data['code'],
                                                        request.user)
            tags = parse_tag_input_local(form.cleaned_data['tags'])
            for tag in tags:
                Tag.objects.add_tag(code, tag)
            return http.HttpResponseRedirect(reverse('code-view',  args=[question.id]))
    else:
        form = forms.CodeForm()
    return shortcuts.render_to_response(
                'projects/contribute.html', 
                {'form':form}, 
                context_instance = RequestContext(request),
    )

def view(request, code_id):
    user = request.user
    code = get_object_or_404(models.Code, id = code_id)
    
    return shortcuts.render_to_response(
                'projects/view.html', 
                {'code':code,    
                 'is_owner':code.user.id == user.id,
                 }, 
                context_instance = RequestContext(request),
    )