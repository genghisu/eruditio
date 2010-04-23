import django.http as http
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from django_badges.models import Badge, BadgeInstance

def view(request, badge_id):
    """
    Paginated list of all users that have been awarded at least one 
    BadgeInstance associated with Badge (id = badge_id).
    """
    badge = Badge.objects.get(id = badge_id)
    users = Badge.objects.users_with_badge(badge)
    
    return shortcuts.render_to_response('django_badges/view.html',
                                        {'users':users,
                                         'badge':badge},
                                         context_instance = RequestContext(request))

def browse(request):
    """
    Simple list of all the Badge objects that have been defined.
    """
    badges = Badge.objects.badges_with_count()
    
    return shortcuts.render_to_response(
        'django_badges/browse.html', 
        {'badges':badges}, 
        context_instance = RequestContext(request),
    )
