from django.http import HttpResponse, HttpResponseRedirect, get_host
from django.shortcuts import render_to_response as render
from django.template import RequestContext
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django_utils.request_helpers import get_redirect_path
import django_openidconsumer.config
import md5, re, time, urllib

import openid   
if openid.__version__ < '2.0.0':
    raise ImportError, 'You need python-openid 2.0.0 or newer'
elif openid.__version__ < '2.1.0':
    from openid import sreg as oidsreg
else: 
    from openid.extensions import sreg as oidsreg
    from openid.extensions import pape as oidpape
    from openid.extensions import ax as oidax

from openid.consumer.consumer import Consumer, \
    SUCCESS, CANCEL, FAILURE, SETUP_NEEDED
from openid.consumer.discover import DiscoveryFailure
from yadis import xri

from util import OpenID, DjangoOpenIDStore, from_openid_response
from middleware import OpenIDMiddleware

from django.utils.html import escape

def get_url_host(request):
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    host = escape(get_host(request))
    return '%s://%s' % (protocol, host)

def get_full_url(request):
    return get_url_host(request) + request.get_full_path()

def is_valid_next_url(request, next):
    # When we allow this:
    #   /openid/?next=/welcome/
    # For security reasons we want to restrict the next= bit to being a local 
    # path, not a complete URL.
    absUri = request.build_absolute_uri(next)
    return absUri != next

def begin(request, user_url, redirect_to=None, next = None, on_failure=None, template_name='openid_signin.html'):
    
    on_failure = on_failure or default_on_failure
    
    trust_root = getattr(
        settings, 'OPENID_TRUST_ROOT', get_url_host(request) + '/'
    )

    redirect_to = redirect_to or getattr(
        settings, 'OPENID_REDIRECT_TO',
        get_full_url(request).split('?')[0] + 'complete/'
    )

    if not redirect_to.startswith('http://') or redirect_to.startswith('https://'):
        redirect_to =  get_url_host(request) + redirect_to
    
    if next and is_valid_next_url(request, next):
        redirect_to += '?' + urllib.urlencode({'redirect': next})
    
    if xri.identifierScheme(user_url) == 'XRI' and getattr(
        settings, 'OPENID_DISALLOW_INAMES', False
        ):
        return on_failure(request, _('i-names are not supported'))
    
    consumer = Consumer(request.session, DjangoOpenIDStore())

    try:
        auth_request = consumer.begin(user_url)
    except DiscoveryFailure:
        return on_failure(request, _('The OpenID was invalid'))
    
    ########## OPENID-PAPE ###########
    if django_openidconsumer.config.OPENID_PAPE:
        if openid.__version__ <= '2.0.0' and openid.__version__ >= '2.1.0':
            raise ImportError, 'For pape extension you need python-openid 2.1.0 or newer'
        p = oidpape.Request()
        for parg in django_openidconsumer.config.OPENID_PAPE:
            if parg.lower().strip() == 'policy_list':
                for v in pape[parg].split(','):
                    p.addPolicyURI(v)
            elif parg.lower().strip() == 'max_auth_age':
                p.max_auth_age = pape[parg]
        auth_request.addExtension(p)
    
    ########## OPENID-AX ##############
    if django_openidconsumer.config.OPENID_AX:
        axr = oidax.FetchRequest()
        for i in django_openidconsumer.config.URI_GROUPS.values():
            axr.add(oidax.AttrInfo(i['type_uri'], i['count'], i['required'], i['alias']))
        auth_request.addExtension(axr)
    
    redirect_url = auth_request.redirectURL(trust_root, redirect_to)
    return HttpResponseRedirect(redirect_url)
    
def complete(request, on_success=None, on_failure=None, failure_template='openid_failure.html'):
    on_success = on_success or default_on_success
    on_failure = on_failure or default_on_failure
    
    consumer = Consumer(request.session, DjangoOpenIDStore())
    
    # JanRain library raises a warning if passed unicode objects as the keys, 
    # so we convert to bytestrings before passing to the library
    query_dict = dict([
        (k.encode('utf8'), v.encode('utf8')) for k, v in request.GET.items()
    ])

    url = get_url_host(request) + request.path
    openid_response = consumer.complete(query_dict, url)
    
    if openid_response.status == SUCCESS:
        return on_success(request, openid_response.identity_url, openid_response)
    elif openid_response.status == CANCEL:
        return on_failure(request, _('The request was cancelled'), failure_template)
    elif openid_response.status == FAILURE:
        return on_failure(request, openid_response.message, failure_template)
    elif openid_response.status == SETUP_NEEDED:
        return on_failure(request, _('Setup needed'), failure_template)
    else:
        assert False, "Bad openid status: %s" % openid_response.status

def default_on_success(request, identity_url, openid_response):
    if 'openids' not in request.session.keys():
        request.session['openids'] = []
    
    # Eliminate any duplicates
    request.session['openids'] = [
        o for o in request.session['openids'] if o.openid != identity_url
    ]
    request.session['openids'].append(from_openid_response(openid_response))
    
    # Set up request.openids and request.openid, reusing middleware logic
    OpenIDMiddleware().process_request(request)
    
    next = get_redirect_path(request)
    if not next or not is_valid_next_url(request, next):
        next = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')
    
    return HttpResponseRedirect(next)

def default_on_failure(request, message, template_name='openid_failure.html'):
    return render(template_name, {
        'message': message
    })

def signout(request):
    request.session['openids'] = []
    next = request.GET.get('next', '/')
    if not is_valid_next_url(request, next):
        next = '/'
    return HttpResponseRedirect(next)
