import openid
if openid.__version__ < '2.0.0':
    raise ImportError, 'You need python-openid 2.0.0 or newer'
elif openid.__version__ < '2.1.0':
    from openid import sreg as oidsreg
else: 
    from openid.extensions import sreg as oidsreg
    from openid.extensions import pape as oidpape
    from openid.extensions import ax as oidax

from openid.store import nonce as oid_nonce
from openid.store.interface import OpenIDStore
from openid.association import Association as OIDAssociation
from yadis import xri

import time, base64, md5

import django_openidconsumer.config
from django.conf import settings
from models import Association, Nonce

class OpenID(object):
    def __init__(self, openid, issued, attrs=None, sreg=None, pape=None, ax=None):
        self.openid = openid
        self.issued = issued
        self.attrs = attrs or {}
        self.sreg = sreg or {}
        self.pape = pape or {}
        self.ax = ax or {}
        self.is_iname = (xri.identifierScheme(openid) == 'XRI')
    
    def __repr__(self):
        return '<OpenID: %s>' % self.openid
    
    def __str__(self):
        return self.openid

class DjangoOpenIDStore(OpenIDStore):
    def __init__(self):
        self.max_nonce_age = 6 * 60 * 60 # Six hours
    
    def storeAssociation(self, server_url, association):
        assoc = Association(
            server_url = server_url,
            handle = association.handle,
            secret = base64.encodestring(association.secret),
            issued = association.issued,
            lifetime = association.issued,
            assoc_type = association.assoc_type
        )
        assoc.save()
    
    def getAssociation(self, server_url, handle=None):
        assocs = []
        if handle is not None:
            assocs = Association.objects.filter(
                server_url = server_url, handle = handle
            )
        else:
            assocs = Association.objects.filter(
                server_url = server_url
            )
        if not assocs:
            return None
        associations = []
        for assoc in assocs:
            association = OIDAssociation(
                assoc.handle, base64.decodestring(assoc.secret), assoc.issued,
                assoc.lifetime, assoc.assoc_type
            )
            if association.getExpiresIn() == 0:
                self.removeAssociation(server_url, assoc.handle)
            else:
                associations.append((association.issued, association))
        if not associations:
            return None
        return associations[-1][1]
    
    def removeAssociation(self, server_url, handle):
        assocs = list(Association.objects.filter(
            server_url = server_url, handle = handle
        ))
        assocs_exist = len(assocs) > 0
        for assoc in assocs:
            assoc.delete()
        return assocs_exist
    
    def storeNonce(self, nonce):
        nonce, created = Nonce.objects.get_or_create(
            nonce = nonce, defaults={'expires': int(time.time())}
        )
    
    def useNonce(self, server_url, timestamp, salt):
        if abs(timestamp - time.time()) > oid_nonce.SKEW:
            return False
        
        try:
            nonce = Nonce( server_url=server_url, timestamp=timestamp, salt=salt)
            nonce.save()
        except:
            raise
        else:
            return 1
    
    def getAuthKey(self):
        # Use first AUTH_KEY_LEN characters of md5 hash of SECRET_KEY
        return md5.new(settings.SECRET_KEY).hexdigest()[:self.AUTH_KEY_LEN]

def from_openid_response(openid_response):
    issued = int(time.time())

    openid = OpenID(openid_response.identity_url, issued, openid_response.signed_fields)

    if django_openidconsumer.config.OPENID_PAPE:
        openid.pape = oidpape.Response.fromSuccessResponse(openid_response)

    if django_openidconsumer.config.OPENID_SREG:
        openid.sreg = oidsreg.SRegResponse.fromSuccessResponse(openid_response)

    if django_openidconsumer.config.OPENID_AX:
        openid.ax = oidax.FetchResponse.fromSuccessResponse(openid_response, False)

    return openid
