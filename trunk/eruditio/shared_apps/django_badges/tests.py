import unittest

from django.contrib.auth.models import User
from django_badges.models import Badge, BadgeInstance
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

class Tests(unittest.TestCase):
    def setUp(self):
        try:
            test_user = User.objects.get(username = 'test_user')
        except ObjectDoesNotExist:
            test_user = User.objects.create_user(username = 'test_user',
                                                 email = 'test_user@test.com',
                                                 password = None)
        self.user = test_user
        
        try:
            test_badge = Badge.objects.get(name = 'Test Badge')
        except ObjectDoesNotExist:
            test_badge = Badge(name = 'Test Badge')
            test_badge.save()
        self.badge = test_badge
        
        try:
            handlerless_badge = Badge.objects.get(name = 'Handlerless Badge')
        except ObjectDoesNotExist:
            handlerless_badge = Badge(name = 'Handlerless Badge')
            handlerless_badge.save()
        self.handlerless_badge = handlerless_badge
        
    def tearDown(self):
        self.user.delete()
        self.badge.delete()
        self.handlerless_badge.delete()
    
    def test_create_badge(self):
        """
        Tests creation of a BadgeInstance.
        """
        instance = Badge.objects.create_badge(badge = self.badge,
                                              user = self.user,
                                              content_type = ContentType.objects.get_for_model(User),
                                              object_id = self.user.id)
        self.assertTrue(BadgeInstance.objects.filter(badge = self.badge))
        instance.delete()
        
    def test_badges_with_count(self):
        """
        Tests retrieving Badge objects with the correponding number of
        BadgeInstances associated with each.
        """
        for i in range(1, 101):
            Badge.objects.create_badge(badge = self.badge,
                                       user = self.user,
                                       content_type = ContentType.objects.get_for_model(User),
                                       object_id = self.user.id)
        self.assertEqual([badge for badge in Badge.objects.badges_with_count() if badge.name == 'Test Badge'][0].count, 100)
        all_badges = BadgeInstance.objects.all()
        for instance in all_badges:
            instance.delete()
    
    def test_badge_registration(self):
        """
        Tests registration of Badge handlers found in handlers.py.
        """
        import django_badges.handlers as handlers
        setattr(handlers, 'TestBadge', type('TestBadge', (object, ), {}))
        
        from django_badges.badges import badges_registry
        import django_badges.badges
        badges_registry = django_badges.badges.BadgesRegistry()
        
        self.assertEqual(badges_registry._handlers.get('Test Badge', None).__class__, handlers.TestBadge)
        self.assertEqual(badges_registry._handlers.get('Handlerless Badge', 'WASSUP'), None)
        
    def test_users_with_badge(self):
        """
        Tests retrieving all users who have obtained a given Badge.
        """
        instance = Badge.objects.create_badge(badge = self.badge,
                                              user = self.user,
                                              content_type = ContentType.objects.get_for_model(User),
                                              object_id = self.user.id)
        self.assertTrue(self.user in Badge.objects.users_with_badge(self.badge))
        instance.delete()

class HandlerTests(unittest.TestCase):
    """
    Tests for site specific handlers go here.
    """
    def setUp(self):
        pass