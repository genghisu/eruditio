import re

import django.http as http
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
import django.utils

from tagging.models import Tag, TaggedItem
from django_metatagging.utils import tagged_objects, parse_tag_input_local, all_tagged_objects
import django_utils.pagination as pagination
import django_utils.request_helpers as request_helpers
import django_contenthistory.signals as signals
import django_metatagging.config as settings

def objects_with_tag(request, content_type, tag, related_tags = False):
    if content_type == "-1":
        return http.HttpResponseRedirect(reverse('all-objects-with-tag', args=[tag]))
    
    page = request_helpers.get_page(request)
    sort = request_helpers.get_sort(request,  'most_popular')
    
    content_type_object = ContentType.objects.get(id = content_type)
    objects, related_tags_list = tagged_objects(content_type, tag, related_tags)
    current_page,  page_range = pagination.paginate_queryset(objects,  10,  5,  page)
    safe_tag = django.utils.http.urlquote(tag)
    
    return shortcuts.render_to_response('django_metatagging/objects_with_tag.html',
                                        {'current_page':current_page,
                                         'node_content_type':content_type_object.id,
                                         'model':content_type_object.model,
                                         'page_range':page_range, 
                                         'tag':tag},
                                        context_instance = RequestContext(request))
    
def all_objects_with_tag(request, tag, related_tags = False):
    page = request_helpers.get_page(request)
    sort = request_helpers.get_sort(request,  'most_popular')
    
    objects, related = all_tagged_objects(tag)
    current_page,  page_range = pagination.paginate_queryset(objects,  10,  5,  page)
    
    return shortcuts.render_to_response('django_metatagging/all_objects_with_tag.html',
                                        {'current_page':current_page, 
                                         'page_range':page_range, 
                                         'tag':tag},
                                        context_instance = RequestContext(request))
    
def browse(request):
    page = request_helpers.get_page(request)
    tags = Tag.objects.all().order_by('name')
    
    current_page, page_range = pagination.paginate_queryset(tags, 50, 5, page)
    current_tags = current_page.object_list
    current_tags = Tag.meta_objects.count_tags(current_tags)
        
    return shortcuts.render_to_response(
        'django_metatagging/browse.html', 
        {'current_page':current_page,  
         'page_range':page_range
        }, 
        context_instance = RequestContext(request), 
    )

def browse_ajax(request,  tag):
    page = request_helpers.get_page(request)
    escaped_tag = re.escape(tag.strip()[1:-1])
    pattern = "^%s.*" % (escaped_tag)
    tags = Tag.objects.filter(name__iregex = pattern).order_by('name')
    
    current_page, page_range = pagination.paginate_queryset(tags, 50, 5, page)
    current_tags = current_page.object_list
    current_tags = Tag.meta_objects.count_tags(current_tags)
        
    return shortcuts.render_to_response(
        'django_metatagging/browse_ajax.html', 
        {'current_page':current_page,  
         'page_range':page_range
        }, 
        context_instance = RequestContext(request), 
    )

class RetagAction(object):
    def __init__(self, model, form_builder, template = None, redirect_url = None):
        self.model = model
        self.form_builder = form_builder
        self.template = template
        self.redirect_url = redirect_url
        self.content_type = ContentType.objects.get_for_model(model)
    
    def __call__(self, request, object_id):
        from django_metatagging.forms import build_retag_form
        user = request.user
        
        object = get_object_or_404(self.model, id = object_id)
        EditForm = self.form_builder(object, disabled = True)
        RetagForm = build_retag_form(object)
        
        if request.POST:
            base_form = EditForm()
            form = RetagForm(request.POST)
            if form.is_valid():
                tags = parse_tag_input_local(form.cleaned_data['tags'])
                original, current = Tag.meta_objects.retag(object, tags)
                
                original_object = object
                current_object = get_object_or_404(self.model, id = object_id)
                setattr(original_object, 'tags', original)
                setattr(current_object, 'tags', current)
                signals.edit.send(sender=self.model, original=original_object, current=current_object, editor=user)
                return http.HttpResponseRedirect(reverse(self.redirect_url, args=[object.id]))
        else:
            base_form = EditForm()
            form = RetagForm()
            
        return shortcuts.render_to_response(
                self.template,
                {'form':form, 
                 'base_form':base_form,
                 'object_id':object.id, 
                 'node':object,
                 'object_url':reverse(self.redirect_url, args=[object.id]),
                 'model':self.content_type.model},
                context_instance = RequestContext(request)
        )