import django.http as http
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

import django_community.models
import django_community.utils
import django_community.forms
from django_utils.pagination import paginate_queryset, paginate_queryset_ajax
from django_utils import request_helpers
import django_utils.pagination as pagination
import django_community.decorators as django_community_decorators
import django_openidconsumer.util, django_openidconsumer.views
import django_community.config as app_config
from django_community.utils import handle_signup, handle_login
from django_community.forms import LoginForm, SignupForm

def combined_logout(request):
    """
    Handles logout both for OpenID and standard authentication.
    """
    django_community.utils.handle_logout(request)
    django_community.utils.openid_logout(request)
    path = request_helpers.get_redirect_path(request)
    if path.strip():
        return http.HttpResponseRedirect(path)
    else:
        return http.HttpResponseRedirect(reverse('main'))

def combined_login(request):
    """
    Handles login view by redirecting to OpenID login if it is enabled, else
    default to standard login via DB backend authentication.
    """
    if app_config.OPENID_ENABLED:
        return http.HttpResponseRedirect(request_helpers.append_redirect_path(reverse('openid-login'),  request))
    else:
        return http.HttpResponseRedirect(request_helpers.append_redirect_path(reverse('community-login'),  request))
    
def openid_login(request, base_error = None):
    """
    Handles OpenID login via form rendering and submission.
    """
    path = request_helpers.get_redirect_path(request)
    if request.POST:
        openid = request.POST.get('openid_identifier', '')
        if openid.strip():
            return django_openidconsumer.views.begin(request,
                                                    openid,
                                                    redirect_to = reverse('openid-complete'),
                                                    next = request_helpers.get_redirect_path(request),
                                                    on_failure = openid_login,
                                                    template_name = 'django_community/openid_login.html')
        else:
            error = 'empty_id'
    else:
        error = base_error
    return shortcuts.render_to_response(
        'django_community/openid_login.html', 
        {'error':error,
         'redirect':path}, 
        context_instance = RequestContext(request),
    )

def openid_complete(request):
    """
    Completes OpenID login process.
    """
    return django_openidconsumer.views.complete(request, on_failure = openid_login)

def openid_logout(request):
    """
    Removes OpenID credentials from session.
    """
    django_community.utils.openid_logout()
    redirect_url = reverse('main')
    return http.HttpResponseRedirect(redirect_url)
    
def user_required(request):
    return shortcuts.render_to_response('django_community/user_required.html',  {},  context_instance = RequestContext(request))
    
def anonymous_required(request):
    return shortcuts.render_to_response('django_community/anonymous_required.html',  {},  context_instance = RequestContext(request))

def profile(request,  user_id,  user_name):
    """
    Gathers and displays user profile data.
    """
    from django_community.config import PROFILES_ENABLED, PROFILE_TEMPLATE
    from django_community.profile_utils import build_profile_information
    
    if PROFILES_ENABLED:
        try:
            user = User.objects.get(id = user_id)
        except ObjectDoesNotExist:
            return http.HttpResponseNotFound()
    
        context = build_profile_information(user)
        user = context['user']
        user = django_community.models.UserProfile.objects.insert_profile_info(user)
    else:
        return http.HttpResponseNotFound()
    
    return shortcuts.render_to_response(
        PROFILE_TEMPLATE, 
        context, 
        context_instance = RequestContext(request),
    )
    
def edit_profile(request):
    """
    Handles editing of an user's profile.
    """
    user = request.user
    EditProfileForm = django_community.forms.build_edit_profile_form(user)
    
    if request.POST:
        edit_profile_form = EditProfileForm(request.POST,  request.FILES,  request)
        if edit_profile_form.is_valid():
            django_community.models.UserProfile.objects.edit_profile(user, edit_profile_form.cleaned_data)
            return http.HttpResponseRedirect(reverse('community-profile',  args=[user.id,  user.profile.display_name]))
    else:
        edit_profile_form = EditProfileForm()
    return shortcuts.render_to_response(
        'django_community/edit_profile.html', 
        {'user':user,  'edit_profile_form':edit_profile_form}, 
        context_instance = RequestContext(request),
    )
    
def contributed_content(request, user_id, content_type):
    """
    Need to remove this for a core method.
    """
    page = request_helpers.get_page(request)
    
    content_type_object = ContentType.objects.get(id = content_type)
    content_model = content_type_object.model_class()
    
    user_object = shortcuts.get_object_or_404(User,  id = user_id)
    content_objects = content_model.objects.filter(user = user_object)
    current_page,  page_range = paginate_queryset_ajax(content_objects,  10,  5,  page,  "%ss_page_" % (content_type_object.model), 
                            reverse('community-contributed-content',  args=[user_object.id,  content_type_object.id]))
    
    return shortcuts.render_to_response(
                'django_community/elements/generic_contributed_content.html', 
                {'current_page':current_page, 'content_type':content_type_object.id,  'page_range':page_range}, 
                context_instance = RequestContext(request),
    )

def browse_users(request):
    """
    Displays a paginated list of all users sorted by reputation.
    """
    page = request_helpers.get_page(request)
    
    users = User.objects.filter(is_superuser = False).order_by('-reputation__reputation')
    current_page, page_range = pagination.paginate_queryset(users, 30, 5, page)
    
    return shortcuts.render_to_response('django_community/browse.html',
                                        {'current_page':current_page,  
                                        'page_range':page_range},
                                        context_instance = RequestContext(request))

def favorite(request, content_type, object_id):
    """
    Adds an object to a user's list of favorite objects.
    """
    user = request.user
    
    content_type_object = ContentType.objects.get(id = int(content_type))
    object = content_type_object.model_class().objects.get(id = int(object_id))
    current_favorite = django_community.models.Favorite.objects.favorites_for_object(object).filter(user = user)
    
    if current_favorite:
        django_community.models.Favorite.objects.remove(object, user)
    else:
        django_community.models.Favorite.objects.add(object, user)
    
    return shortcuts.render_to_response('django_community/elements/favorite_action.html',
                                         {'node':object,
                                          'node_content_type':content_type,
                                          'already_favorited': not current_favorite},
                                          context_instance = RequestContext(request))

def standard_login(request):
    """
    Handles login for none OpenID users.
    """
    path = request_helpers.get_redirect_path(request)
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            handle_login(request, form.cleaned_data)
            return http.HttpRedirectResponse(path)
    else:
        form = LoginForm()
        
    return shortcuts.render_to_response('django_community/login.html',
                                        {'form':form,
                                         'redirect':path},
                                        context_instance = RequestContext(request))

def standard_signup(request):
    """
    Handles signup for none OpenID users.
    """
    path = request_helpers.get_redirect_path(request)
    if request.POST:
        form = SignupForm(request.POST, request.FILES, request)
        if form.is_valid():
            handle_signup(request, form.cleaned_data)
            return http.HttpRedirectResponse(path)
    else:
        form = SignupForm()
    
    return shortcuts.render_to_response('django_community/signup.html',
                                        {'form':form,
                                         'redirect':path},
                                        context_instance = RequestContext(request))
            
    