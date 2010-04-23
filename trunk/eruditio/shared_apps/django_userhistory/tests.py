import unittest

from django.contrib.auth.models import User
from django_userhistory.models import UserAction, UserHistory

class HistoryTests(unittest.TestCase):
    def setUp(self):
        user_1 = User.objects.create_user(username = 'Test User',
                                          email = 'test_user@gmail.com')
        self.user_1 = user_1
        
        user_2 = User.objects.create_user(username = 'Test User 2',
                                          email = 'test_user@gmail.com')
        self.user_2 = user_2

        edit_action, created = UserAction.objects.get_or_create(name = 'edit')
        self.edit_action = edit_action
        
    def tearDown(self):
        self.user_1.delete()
        self.user_2.delete()
        self.edit_action.delete()
        
    def test_add_user_history(self):
        """
        Tests the creation of a new UserHistory.
        """
        new_history = UserHistory.objects.add_user_history(self.user_1, self.edit_action, self.user_2)
        self.assertTrue(new_history)
        self.assertEqual(new_history.action, self.edit_action)
        self.assertEqual(new_history.object, self.user_2)
        new_history.delete()
        
    def test_get_user_history(self):
        """
        Tests retrieval of all UserHistory objects associated
        with an user.
        """
        new_history = UserHistory.objects.add_user_history(self.user_1, self.edit_action, self.user_2)
        user_histories = UserHistory.objects.user_history(self.user_1)
        self.assertEqual(len(user_histories), 1)
        self.assertEqual(user_histories[0], new_history)
        new_history.delete()