import datetime

from django_community.config import ANONYMOUS_USERS_ENABLED
from django_community.models import UserOpenID, UserProfile
from django_community.utils import create_user_from_openid, get_anon_user, is_anon_user, process_ax_data
from django.core.exceptions import ObjectDoesNotExist

class CommunityMiddleware(object):
    """
    Attaches user object to the request object based on information found
    in the session concerning currently available OpenIDs.  Attaches a 
    UserProfile object to request.user which guarantees the logged in
    user always has a UserProfile (in case it was not generated properly
    for whatever reason).  Also attempts to process any OpenID AX data
    attached to the request.
    """
    def process_request(self, request):
        if not request.user.is_authenticated():
            if request.openid:
                try:
                    user_open_id = UserOpenID.objects.get(openid = request.openid.openid)
                    request.user = user_open_id.user
                except ObjectDoesNotExist:
                    request.user = create_user_from_openid(request, request.openid)
        if not request.user.is_authenticated() and ANONYMOUS_USERS_ENABLED:
            request.user = get_anon_user(request)
        if request.user.is_authenticated():
            request.user.profile = UserProfile.objects.get_user_profile(request.user)
            request.user.last_login = datetime.datetime.now()
            request.user.save()
        if getattr(request.openid, 'ax', None) and request.user.is_authenticated():
            process_ax_data(request.user, request.openid.ax.data)

