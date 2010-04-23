import unittest

from django_comments.models import Comment
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

class Tests(unittest.TestCase):
    def setUp(self):
        try:
            test_user = User.objects.get(username = 'test_user')
        except ObjectDoesNotExist:
            test_user = User.objects.create_user(username = 'test_user',
                                                             email = 'test_user@test.com',
                                                             password = None)
        self.user = test_user
    
    def tearDown(self):
        self.user.delete()
        
    def test_create_comment(self):
        """
        Test comment creation by creating a comment on a user.
        """
        new_comment = Comment.objects.add_comment(self.user, self.user, 'Testing comments for user.', None)
        self.assertEqual(new_comment.content, 'Testing comments for user.')
        self.assertEqual(new_comment.content_object, self.user)
        new_comment.delete()
        
    def test_edit_comment(self):
        """
        Test comment modification through editing.
        """
        new_comment = Comment.objects.add_comment(self.user, self.user, 'Testing comments for user.', None)
        Comment.objects.edit_comment(new_comment, 'Testing comment editing.')
        self.assertEqual(new_comment.content, 'Testing comment editing.')
        new_comment.delete()
    
    def test_comments_for_user(self):
        """
        Test retrieval of comments associated with a user.
        """
        for i in range(1, 21):
            new_comment = Comment.objects.add_comment(self.user, self.user, 'Comment %s' % (str(i)))
        self.assertEqual(Comment.objects.comments_by_user(self.user).count(), 20)
        for comment in Comment.objects.comments_by_user(self.user):
            comment.delete()
    
    def test_comments_for_object(self):
        """
        Test retrieval of comments associated with an object.
        """
        for i in range(1, 21):
            new_comment = Comment.objects.add_comment(self.user, self.user, 'Comment %s' % (str(i)))
        self.assertEqual(Comment.objects.comments_for_object(self.user).count(), 20)
        for comment in Comment.objects.comments_for_object(self.user):
            comment.delete()