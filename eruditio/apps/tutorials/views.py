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
import tutorials.forms as forms
import tutorials.models as models
from django_moderation.views import FlagAction
from django_metatagging.views import RetagAction
from django_reputation.models import Reputation
from django_common.views import ListView, ContributeView, EditView
from django_tracking.models import View

tutorials_list = ListView(model = models.Tutorial,
                         per_page = 20,
                         ordered = True,
                         moderated = False,
                         template = 'tutorials/list.html')

contribute_tutorial = ContributeView(model = models.Tutorial,
                                    form_builder = forms.build_tutorial_form,
                                    redirect_url = 'tutorials-view-tutorial',
                                    template = 'tutorials/contribute.html')

edit_tutorial = EditView(model = models.Tutorial,
                        form_builder = forms.build_tutorial_form,
                        view_url = 'tutorials-view-tutorial',
                        redirect_url = 'tutorials-view-tutorial',
                        template = 'tutorials/edit.html')

def view(request, tutorial_id):
    user = request.user
    tutorial = get_object_or_404(models.Tutorial, id = tutorial_id)
    
    View.objects.add(tutorial, request_helpers.get_ip(request))
    return shortcuts.render_to_response(
                'tutorials/view.html', 
                {'tutorial':tutorial,    
                 'is_owner':tutorial.user.id == tutorial.id,
                 }, 
                context_instance = RequestContext(request),
    )
    
flag_tutorial = FlagAction(models.Tutorial, forms.build_flag_form, 'tutorials/elements/flag_form.html', 'tutorials-view-tutorial')

retag_tutorial = RetagAction(models.Tutorial, forms.build_tutorial_form, 'shared/retag.html', 'tutorials-view-tutorial')
