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
from django_metatagging.views import RetagAction
from django_moderation.views import FlagAction
from django_reputation.models import Reputation

import applications.forms as forms
import applications.models as models
from core.models import DjangoCompatibility, PythonCompatibility, Source
from django_common.views import ListView, ContributeView, EditView

apps_list = ListView(model = models.App,
                     per_page = 20,
                     ordered = True,
                     moderated = True,
                     template = 'applications/list.html')

contribute_app = ContributeView(model = models.App,
                                form_builder = forms.build_app_form,
                                redirect_url = 'applications-view-app',
                                template = 'applications/contribute.html')

edit_app = EditView(model = models.App,
                    form_builder = forms.build_app_form,
                    view_url = 'applications-view-app',
                    redirect_url = 'applications-view-app',
                    template = 'applications/edit.html')

flag_app = FlagAction(models.App, 
                      forms.build_flag_form, 
                      'applications/elements/flag_form.html', 
                      'applications-view-app')

retag_app = RetagAction(models.App, 
                        forms.build_app_form, 
                        'shared/retag.html', 
                        'applications-view-app')

def view_app(request, app_id):
    from django_relatedcontent.models import ContentAssociation
    from django_tracking.models import View
    
    user = request.user
    app = get_object_or_404(models.App, id = app_id)
                                             
    app_content_type = ContentType.objects.get_for_model(models.App)
    dependencies = ContentAssociation.objects.associations_for_object(app, 'dependency', models.App)
    app.dependencies = [models.App.objects.get(id = x.child_object_id) for x in dependencies]
    app.sources = [source.uri for source in Source.objects.filter(content_type = app_content_type,
                                                                  object_id = app_id)]
    app.pythons = PythonCompatibility.objects.filter(content_type = app_content_type,
                                                  object_id = app.id)
    app.djangos = DjangoCompatibility.objects.filter(content_type = app_content_type,
                                                  object_id = app.id)
    
    View.objects.add(app, request_helpers.get_ip(request))
    return shortcuts.render_to_response(
                'applications/view.html', 
                {'app':app,    
                 'is_owner':app.user.id == user.id,
                 }, 
                context_instance = RequestContext(request),
    )

def edit_dependencies(request, app_id):
    user = request.user
    
    app = get_object_or_404(models.App, id = app_id)
    content_type = ContentType.objects.get_for_model(models.App)
    usage, update_mode, associate_url = 'dependency', 'ajax/update', 'django-relatedcontent-modify-association'
    
    return shortcuts.render_to_response(
                'applications/edit_dependencies.html', 
                {'app':app,  
                 'node':app,
                 'model':'app',
                 'object_url':reverse('applications-view-app',  args=[app.id]),
                 'base_content_type':content_type.id,
                 'base_object_id':app.id,
                 'usage':usage,
                 'update_mode':update_mode,
                 'associate_url':associate_url}, 
                context_instance = RequestContext(request),
    )