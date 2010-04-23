import unittest

import django_community.utils as utils
import django_community.config as config
from django_community.models import UserOpenID, UserProfile
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

URI_GROUPS = {u'alias': {u'count': 1, u'alias': u'alias', u'required': True, u'type_uri': u'http://axschema.org/namePerson/friendly'}, u'email': {u'count': 1, u'alias': u'email', u'required': True, u'type_uri': u'http://axschema.org/contact/email'}}
OPENID_FIELD_MAPPING = {u'dob': u'birthdate', u'country': u'location', u'fullname': u'fullname', u'nickname': u'display_name', u'email': u'email'}

class DummyRequest(object):
    def __init__(self):
        self.META = {'REMOTE_ADDR':'192.168.1.1'}

class DummyOpenId(object):
    def __init__(self):
        self.openid = 'Test User'
        self.sreg = {}
        for attribute in OPENID_FIELD_MAPPING.keys():
            mapped_attribute = OPENID_FIELD_MAPPING[attribute]
            self.sreg[attribute] = 'Testing'
        self.ax = {}
        self.ax[URI_GROUPS.get('email').get('type_uri')] = ['hanbox@hanbox.org']
        self.ax[URI_GROUPS.get('alias').get('type_uri')] = ['hanbox']
        
class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.openid = DummyOpenId()
        self.user = utils.get_or_create_from_openid(self.openid.openid)
        self.request = DummyRequest()
        
    def tearDown(self):
        self.user.delete()
    
    def test_create_user(self):
        """
        Checks that an user is created correctly from get_or_create_from_openid
        """
        self.assertEqual(self.user.username, 'Test User')
    
    def test_create_anon_user(self):
        """
        Tests creation of anonymous users.
        """
        anon_user = utils.create_anon_user(self.request)
        self.assertEqual(anon_user.profile.display_name, 'anonymous')
        self.assertEqual(anon_user.username, "anon_user_%s" % (str(self.request.META.get('REMOTE_ADDR'))))
        anon_user.delete()
        
    def test_create_from_openid(self):
        """
        Tests creation of a new user from an OpenID.
        """
        user = utils.create_user_from_openid(self.request, self.openid)
        openids = UserOpenID.objects.filter(user = user)
        self.assertTrue(user)
        self.assertTrue(openids)
        self.assertTrue(self.openid.openid in [x.openid for x in openids])
        user.delete()
        
    def test_get_or_create_profile(self):
        """
        Tests get_user_profile from UserProfileManager.
        """
        new_user = User(username = 'Profile User')
        new_user.save()
        user_profile = UserProfile.objects.get_user_profile(new_user)
        self.assertTrue(new_user.profile)
        self.assertEqual(new_user.username, new_user.profile.display_name)
        new_user.delete()
        
    def test_generate_random_user(self):
        """
        Tests generation of random user names.
        """
        username = utils.generate_random_user_name()
        self.assertTrue(utils.is_random(username))
    
    def test_process_ax_data(self):
        """
        Tests integration of OpenID AX data with the current user's profile.
        """
        new_user = User(username = utils.generate_random_user_name())
        new_user.save()
        user_profile = UserProfile.objects.get_user_profile(new_user)
        utils.process_ax_data(new_user, self.openid.ax)
        user_profile = UserProfile.objects.get_user_profile(new_user)
        self.assertEqual(new_user.profile.display_name, 'hanbox')
        self.assertEqual(new_user.email, 'hanbox@hanbox.org')
        new_user.delete()