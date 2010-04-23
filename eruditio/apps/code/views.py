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
import code.forms as forms
import code.models as models
from django_metatagging.views import RetagAction
from django_moderation.views import FlagAction
from django_common.views import ListView, ContributeView, EditView
from django_tracking.models import View

code_list = ListView(model = models.Code,
                     per_page = 20,
                     ordered = True,
                     moderated = True,
                     template = 'code/list.html')

contribute_code = ContributeView(model = models.Code,
                                form_builder = forms.build_code_form,
                                redirect_url = 'code-view-code',
                                template = 'code/contribute.html')

edit_code = EditView(model = models.Code,
                    form_builder = forms.build_code_form,
                    view_url = 'code-view-code',
                    redirect_url = 'code-view-code',
                    template = 'code/edit.html')

flag_code = FlagAction(models.Code, 
                       forms.build_flag_form, 
                       'code/elements/flag_form.html', 
                       'code-view')

retag_code = RetagAction(models.Code, 
                         forms.build_code_form, 
                         'shared/retag.html', 
                         'code-view')

def view(request, code_id):
    user = request.user
    code = get_object_or_404(models.Code, id = code_id)
    
    View.objects.add(code, request_helpers.get_ip(request))
    return shortcuts.render_to_response(
                'code/view.html', 
                {'code':code,    
                 'is_owner':code.user.id == user.id,
                 }, 
                context_instance = RequestContext(request),
    )

def view_full(request, code_id):
    user = request.user
    code = get_object_or_404(models.Code, id = code_id)
    
    return shortcuts.render_to_response(
                'code/view_full.html', 
                {'code':code,    
                 'is_owner':code.user.id == user.id,
                 }, 
                context_instance = RequestContext(request),
    )