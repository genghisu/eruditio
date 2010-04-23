import unittest
import datetime

from django.contrib.auth.models import User
from django_multivoting.models import Vote, Popularity
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

class Tests(unittest.TestCase):
    def setUp(self):
        try:
            test_user = User.objects.get(username = 'Test User')
        except ObjectDoesNotExist:
            test_user = User.objects.create_user(username = 'Test User',
                                                 email = 'test_user@gmail.com')
        self.user = test_user
        
        try:
            test_user_2 = User.objects.get(username = 'Test User 2')
        except ObjectDoesNotExist:
            test_user_2 = User.objects.create_user(username = 'Test User 2',
                                                   email = 'test_user2@gmail.com')
        self.test_user = test_user_2
    
    def tearDown(self):
        self.test_user.delete()
        self.user.delete()
        for vote in Vote.objects.all():
            vote.delete()
        for popularity in Popularity.objects.all():
            popularity.delete()
            
    def test_handle_vote(self):
        """
        Tests creation of new votes.
        """
        status = Vote.objects.handle_vote(self.user, self.user, Vote.UP)
        self.assertTrue(status)
        self.assertEqual(Vote.objects.votes_for_user(self.user), 1)
        self.assertEqual(Vote.objects.votes_for_object(self.user, Vote.UP), 1)
        
        status = Vote.objects.handle_vote(self.user, self.test_user, Vote.DOWN)
        self.assertTrue(status)
        self.assertEqual(Vote.objects.votes_for_user(self.user), 2)

    def test_most_active(self):
        """
        Tests retrieval of most active instances of a model.
        """
        status = Vote.objects.handle_vote(self.user, self.user, Vote.UP)
        status = Vote.objects.handle_vote(self.user, self.test_user, Vote.UP)
        last_week = datetime.date(1,  1,  1).today() - datetime.timedelta(days = 7)
        most_active_objects = Vote.objects.most_active_objects(User, last_week, 10)
        
        self.assertTrue(most_active_objects)
        self.assertEqual(most_active_objects.count(), 3)
        self.assertEqual(most_active_objects[0], self.user)
        
    def test_most_popular(self):
        """
        Tests retrieval of most popular instances of a model.
        """
        status = Vote.objects.handle_vote(self.user, self.user, Vote.UP)
        status = Vote.objects.handle_vote(self.user, self.test_user, Vote.UP)
        most_popular_objects = Vote.objects.most_popular_objects(User, 10)
        
        self.assertTrue(most_popular_objects)
        self.assertEqual(most_popular_objects.count(), 3)
        self.assertEqual(most_popular_objects[0], self.user)
        
    def test_votes_for_object(self):
        """
        Tests retrieval of all votes associated with an object.
        """
        status = Vote.objects.handle_vote(self.user, self.user, Vote.UP)
        status = Vote.objects.handle_vote(self.test_user, self.user, Vote.UP)
        vote_count = Vote.objects.votes_for_object(self.user, Vote.UP)
        self.assertEqual(vote_count, 2)
    
    def test_votes_for_user(self):
        """
        Tests retrieval of all votes a user has cast.
        """
        status = Vote.objects.handle_vote(self.user, self.user, Vote.UP)
        status = Vote.objects.handle_vote(self.user, self.test_user, Vote.UP)
        vote_count = Vote.objects.votes_for_user(self.user)
        self.assertEqual(vote_count, 2)
    
    def test_popularity(self):
        """
        Tets retrieval of an object's popularity.
        """
        popularity = Vote.objects.popularity(self.test_user)
        self.assertEqual(popularity.popularity, 0)
        status = Vote.objects.handle_vote(self.user, self.test_user, Vote.UP)
        popularity = Vote.objects.popularity(self.test_user)
        self.assertEqual(popularity.popularity, 1)
    
    def test_voted_objects_by_user(self):
        """
        Tests retrieval of all objects a user has cast at least
        one vote on.
        """
        status = Vote.objects.handle_vote(self.user, self.user, Vote.UP)
        status = Vote.objects.handle_vote(self.user, self.test_user, Vote.UP)
        voted_objects = Vote.objects.voted_objects_by_user(self.user, User)
        
        self.assertEqual(voted_objects.count(), 2)
    
    def test_update_popularity(self):
        """
        Tests updating an object's popularity.
        """
        popularity = Vote.objects.popularity(self.user)
        self.assertEqual(popularity.popularity, 0)
        new_vote = Vote(content_type = ContentType.objects.get_for_model(User), 
                        object_id = self.user.id, 
                        mode = Vote.UP, 
                        user = self.test_user)
        new_vote.save()
        updated_popularity = Vote.objects.update_popularity(self.user)
        self.assertEqual(updated_popularity.popularity, 1)