from django.db.models.signals import post_save
from django.db import models
from django_badges.models import BadgeInstance, Badge
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

class StandardBadge(object):
    """
    Parent class from which all Badge handler classes in handlers.py should inherit from.
    
    Defines the complete set of methods that any Badge handler class should define
    in order to correctly handle the post_save events that have been registered 
    by the handler.
    
    @name - name of Badge that this handler corresponds to
    @unique_for_user -  True if only one instance of a Badge can be awarded to an user
    @unique_for_instance - True if only one instance of a Badge can be awarded for the target object
    @model - Django model that will be tracked by the post_save signal receiver defined in the handler.
    """
    name = None
    unique_for_user = True
    unique_for_instance = True
    model = models.Model
    
    def __init__(self):
        post_save.connect(self._signal_callback, sender=self.model, weak = False)
    
    def _signal_callback(self, **kwargs):
        """
        Called when a post_save signal gets raised by self.model.
        """
        i = kwargs['instance']
        self.award(i)
    
    def _can_award(self, instance, user):
        """
        Returns True if the Badge can be awarded to the user else return False.
        
        Checks for self.unique_for_user and self.unique_for_instance conditions.
        """
        status = True
        if self.unique_for_user and self._get_badge_instances_for_user(user):
            status = False
        if self.unique_for_instance and self._get_badge_instances_for_object(instance):
            status = False
        return status 
    
    def _get_badge(self):
        """
        Returns the Badge object associated with this handler.
        """
        try:
            badge_object = Badge.objects.get(name = self.name)
        except ObjectDoesNotExist:
            badge_object = None
        return badge_object
    
    def _get_badge_instances_for_object(self, instance):
        """
        Return all the BadgeInstances that are associated with a target object.
        """
        badge_object = self._get_badge()
        content_type_object = ContentType.objects.get_for_model(instance.__class__)
        object_id = instance.id
        return BadgeInstance.objects.filter(badge = badge_object, content_type = content_type_object, object_id = object_id)
    
    def _get_badge_instances_for_user(self, user):
        """
        Return all the BadgeInstances associated with a target user.
        """
        badge_object = self._get_badge()
        return BadgeInstance.objects.filter(badge = badge_object, user = user)
    
    def check_conditions(self, instance, user):
        """
        Determine whether conditions have been fulfilled in order to award a new Badge.
        """
        return False
    
    def get_user(self, instance):
        """
        Given the instance of the saved object, return the user associated with the instance.
        """
        return getattr(instance, 'user', None)
    
    def get_target_object(self, instance):
        """
        Returns the target object associated with the post_save event.
        """
        return instance
    
    def create_badge(self, instance, user):
        """
        Creates a new BadgeInstance.
        """
        badge_object = self._get_badge()
        target_object = self.get_target_object(instance)
        content_type_object = ContentType.objects.get_for_model(target_object.__class__)
        object_id = target_object.id
        badge_instance = Badge.objects.create_badge(user = user,
                                                    content_type = content_type_object,
                                                    object_id = object_id,
                                                    badge = badge_object)
        return badge_instance
    
    def award(self, instance):
        """
        Attempts to award a Badge by creating a new BadgeInstance if the
        target conditions have been met.
        """
        user = self.get_user(instance)
        if self._can_award(instance, user) and self.check_conditions(instance, user):
            self.create_badge(instance, user)

class TagBadge(object):
    """
    badge for being proficient in a certain set of tags
    """
    pass

    