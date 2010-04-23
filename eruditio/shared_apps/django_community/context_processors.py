from django_community.models import UserProfile

from django_utils.request_helpers import get_ip
from django_community.utils import get_anon_user, is_anon_user

def community(request):
    """
    Exposes authentication context variables.
    
    @var community_user - User who is currently logged in, None if no one is logged in.
    @var islogged - True if a user is logged in.
    @var isAnon - True if an anonymous user is using the site.
    """
    user = request.user
    return {'community_user':user,  'islogged':user.is_authenticated(), 'isAnon':is_anon_user(request.user)}