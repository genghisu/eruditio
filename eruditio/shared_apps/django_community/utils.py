"""
Various utilities functions used by django_community and
other apps to perform authentication related tasks.
"""

import hashlib, re

import django.forms as forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ValidationError
import django.http as http
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth import logout as auth_logout
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
    
from django_community.models import UserOpenID, UserProfile

def openid_logout(request):
    """
    Clears session which effectively logs out the current
    OpenId user.
    """
    request.session.flush()
    
def handle_logout(request):
    """
    Log out.
    """
    auth_logout(request)
    
def get_logged_user(request):
    """
    Returns the current user who is logged in, checks for openid user first, 
    then for regular user, return None if no user is currently logged in
    """
    if settings.OPENID_ENABLED and hasattr(request, 'openid'):
        user = UserOpenID.objects.get_for_openid(request, request.openid)
    if not user:
        user = request.user
    return user

def handle_login(request, data):
    """
    Logs the user in based on form data from django_community.LoginForm.
    """
    user = authenticate(username = data.get('username', None),
                        password = data.get('password', None))
    user_object = User.objects.get(username = data.get('username', None))
    if user is not None:
        login(request, user)
    return user
        
def handle_signup(request,  data):
    """
    Signs a user up based on form data from django_community.SignupForm.
    """
    from django.contrib.auth.models import get_hexdigest
    
    username = data.get('username', None)
    email = data.get('email', None)
    password = data.get('password', None)
    
    try:
        user = User.objects.get(username = username,  email = email)
    except ObjectDoesNotExist:
        user = User(username = username,  email = email)
        user.save()
        user.set_password(password)
        user_profile = UserProfile.objects.get_user_profile(user)
    
    user = authenticate(username = username, password = password)
    login(request, user)
    return user

def get_or_create_from_openid(openid):
    """
    Returns an User with the given openid or
    creates a new user and associates openid with that user.
    """
    try:
        user = User.objects.get(username = openid)
    except ObjectDoesNotExist:
        password = hashlib.sha256(openid).hexdigest()
        user = User(username = openid,  email = '',  password = password)
        user.save()
        user.display_name = "%s_%s" % ('user',  str(user.id))
        user.save()
    
    return user

def generate_random_user_name():
    """
    Generates a random user name user_{user_id}_{salt}
    to be used for creating new users.
    """
    import random
    
    current_users = User.objects.all().order_by('-id')
    if current_users:
        next_id = current_users[0].id + 1
    else:
        next_id = 1
    random_salt = random.randint(1, 5000)
    return 'user_%s_%s' % (str(next_id), str(random_salt))

def create_user_from_openid(request, openid):
    """
    Creates a new User object associated with the given
    openid.
    """
    from django_community.config import OPENID_FIELD_MAPPING
    from django_utils.request_helpers import get_ip
    
    username = generate_random_user_name()
    profile_attributes = {}
    for attribute in OPENID_FIELD_MAPPING.keys():
        mapped_attribute = OPENID_FIELD_MAPPING[attribute]
        if openid.sreg and openid.sreg.get(attribute, ''):
            profile_attributes[mapped_attribute] = openid.sreg.get(attribute, '')
            
    new_user = User(username = username)
    new_user.save()
    new_openid = UserOpenID(openid = openid.openid, user = new_user)
    new_openid.save()
    new_user_profile = UserProfile.objects.get_user_profile(new_user)
    for filled_attribute in profile_attributes.keys():
        setattr(new_user, filled_attribute, profile_attributes[filled_attribute])
    new_user_profile.save()
    return new_user

def get_anon_user(request):
    """
    Returns an anonmymous user corresponding to this IP address if one exists.
    Else create an anonymous user and return it.
    """
    try:
        anon_user = User.objects.get(username = generate_anon_user_name(request))
    except ObjectDoesNotExist:
        anon_user = create_anon_user(request)
    return anon_user
    
def create_anon_user(request):
    """
    Creates a new anonymous user based on the ip provided by the request
    object.
    """
    anon_user_name = generate_anon_user_name(request)
    anon_user = User(username = anon_user_name)
    anon_user.save()
    user_profile = UserProfile(user = anon_user, display_name = 'anonymous')
    user_profile.save()
    return anon_user

def generate_anon_user_name(request):
    """
    Generate an anonymous user name based on and ip address.
    """
    from django_utils.request_helpers import get_ip
    
    ip = get_ip(request)
    return "anon_user_%s" % (str(ip))

def is_anon_user(user):
    """
    Determine if an user is anonymous or not.
    """
    return user.username[0:10] == 'anon_user_'

def is_random(name):
    """
    Determine if a user has a randomly generated display name.
    """
    if len(name.split('_')) and name.startswith('user'):
        return True
    else:
        return False
    
def process_ax_data(user, ax_data):
    """
    Process OpenID AX data.
    """
    import django_openidconsumer.config
    
    emails = ax_data.get(django_openidconsumer.config.URI_GROUPS.get('email').get('type_uri', ''), '')
    display_names = ax_data.get(django_openidconsumer.config.URI_GROUPS.get('alias').get('type_uri', ''), '')
    if emails and not user.email.strip():
        user.email = emails[0]
        user.save()
    if not user.profile.display_name.strip() or is_random(user.profile.display_name):
        if display_names:
            user.profile.display_name = display_names[0]
        elif emails:
            user.profile.display_name = emails[0].split('@')[0]
        user.profile.save()