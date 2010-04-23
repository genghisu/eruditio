"""
Badge handler classes which define the conditions for awarding each individual Badge.

Every handler class subclass django_badges.utils.StandardBadge which contains a set of
sensible methods for handling condition checking of Badge conditions and handling awarding
of Badges.

Each handler object should override check_conditions to specify the conditions under which
the handler will cause a Badge to be rewarded.

The class name of each handler should correspond to the studly caps version of the badge_name 
defined within django_badges.models.Badge.badge_name.  For example the Badge object with
badge_name Citizen Patrol will look for a handler named CitizenPatrol.
"""

try:
    import json
except:
    import simplejson as json

from django_badges.utils import StandardBadge
from django_community.models import UserProfile
from django_moderation.models import ContentFlagVote
from django_multivoting.models import Vote
from django_comments.models import Comment
from django_contenthistory.models import ModelHistory
from django_qa.models import Question, Answer

class Autobiographer(StandardBadge):
    name = "Autobiographer"
    model = UserProfile
    unique_for_user = True
    
    def check_conditions(self, instance, user):
        if instance.website.strip() and instance.birthdate and \
           instance.location.strip() and instance.display_name.strip() and instance.about_me.strip():
            return True
        else:
            return False
        
class CitizenPatrol(StandardBadge):
    name = "Citizen Patrol"
    model = ContentFlagVote
    unique_for_user = True
    
    def check_conditions(self, instance, user):
        return True
    
class CivicDuty(StandardBadge):
    name = "Civic Duty"
    model = Vote
    unique_for_user = True
    
    def get_target_object(self):
        return instance.user
    
    def check_conditions(self, instance, user):
        if Vote.objects.votes_for_user(user) >= 300:
            return True

class Commentator(StandardBadge):
    name = "Commentator"
    model = Comment
    unique_for_user = True
    
    def get_target_object(self, instance):
        return instance.user
    
    def check_conditions(self, instance, user):
        if Comment.objects.comments_by_user(user).count() >= 10:
            return True

class Critic(StandardBadge):
    name = "Critic"
    model = Vote
    unique_for_user = True
    
    def check_conditions(self, instance, user):
        if instance.mode == 'down':
            return True

class Editor(StandardBadge):
    name = "Editor"
    model = ModelHistory
    unique_for_user = True
    
    def check_conditions(self, instance, user):
        if ModelHistory.objects.edits_for_user(user).count() >= 10:
            return True

class Enlightened(StandardBadge):
    name = "Enlightened"
    model = Answer
    unique_for_user = False
    unique_for_instance = True
    
    def check_conditions(self, instance, user):
        if instance.accepted and Vote.objects.votes_for_object(instance, 'up') >= 10:
            return True

class GoodAnswer(StandardBadge):
    name = "Good Answer"
    model = Answer
    unique_for_user = False
    unique_for_instance = True
    
    def check_conditions(self, instance, user):
        if Vote.objects.votes_for_object(instance, 'up') >= 25:
            return True
        
class GoodQuestion(StandardBadge):
    name = "Good Question"
    model = Question
    unique_for_user = False
    unique_for_instance = True
    
    def check_conditions(self, instance, user):
        if Vote.objects.votes_for_object(instance, 'up') >= 25:
            return True
        
class GreatAnswer(StandardBadge):
    name = "Great Answer"
    model = Answer
    unique_for_user = False
    unique_for_instance = True
    
    def check_conditions(self, instance, user):
        if Vote.objects.votes_for_object(instance, 'up') >= 100:
            return True

class GreatQuestion(StandardBadge):
    name = "Great Question"
    model = Question
    unique_for_user = False
    unique_for_instance = True
    
    def check_conditions(self, instance, user):
        if Vote.objects.votes_for_object(instance, 'up') >= 100:
            return True
        
class Guru(StandardBadge):
    name = "Guru"
    model = Answer
    unique_for_user = False
    unique_for_instance = True
    
    def check_conditions(self, instance, user):
        if instance.accepted and Vote.objects.votes_for_object(instance, 'up') >= 50:
            return True
        
class Organizer(StandardBadge):
    name = "Organizer"
    model = ModelHistory
    unique_for_user = True
    
    def check_conditions(self, instance, user):
        if json.loads(instance.data).get('tags', None):
            return True
        
class Student(StandardBadge):
    name = "Student"
    model = Vote
    unique_for_user = True
    
    def get_target_object(self, instance):
        return instance.content_object
    
    def get_user(self, instance):
        target_object = self.get_target_object(instance)
        return target_object.user
    
    def check_conditions(self, instance, user):
        if Vote.objects.votes_for_object(instance, 'up') > 1 and self.get_target_object().__class__ == Question:
            return True

class Scholar(StandardBadge):
    name = "Scholar"
    model = Answer
    unique_for_user = True
    
    def get_user(self, instance):
        return instance.question.user
    
    def check_conditions(self, instance, user):
        if instance.accepted:
            return True
        
class Supporter(StandardBadge):
    name = "Supporter"
    model = Vote
    unique_for_user = True
    
    def check_conditions(self, instance, user):
        if instance.mode == 'up':
            return True
        
class Teacher(StandardBadge):
    name = "Teacher"
    model = Vote
    unique_for_user = True
    
    def get_target_object(self, instance):
        return instance.content_object
    
    def get_user(self, instance):
        target_object = self.get_target_object(instance)
        return target_object.user
    
    def check_conditions(self, instance, user):
        if Vote.objects.votes_for_object(instance, 'up') > 1 and self.get_target_object().__class__ == Answer:
            return True
        