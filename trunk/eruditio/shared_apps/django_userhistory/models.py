from django.db import models

from django_extensions.db.fields import CreationDateTimeField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django_userhistory.exceptions import UserHistoryException

class UserHistoryManager(models.Manager):
    def user_history(self, user, type = None):
        """
        Returns all UserHistory objects associated with a user, filtered by
        type if type is not None.
        """
        if type:
            type_object = self.get_activity_type(type)
            history = self.model.objects.filter(user = user, action = type).order_by('-date_created')
        else:
            history = self.model.objects.filter(user = user).order_by('-date_created')
        return history
    
    def add_user_history(self, user, action, object):
        """
        Create a new UserHistory based on user, action and object params.
        """
        content_type_object = ContentType.objects.get_for_model(object.__class__)
        object_id = object.id
        history = self.model(action = action,
                             user = user,
                             content_type = content_type_object,
                             object_id = object_id)
        history.save()
        return history
    
    def get_activity_type(self, type):
        """
        Helper method for getting the UserAction. If string provided, try as name.
        If type is of class UserAction, return type.
        """
        if type.__class__ == UserAction:
            activity_object = type
        else:
            try:
                activity_object = UserAction.objects.get(name = str(type))
            except Exception, e:
                activity_object = None
                raise UserHistoryException("UserActivityType %s does not exist" % (str(type)))
        return activity_object
    
class UserAction(models.Model):
    """
    Types of actions being tracked.
    """
    name = models.CharField(max_length = 75)
    
    def __unicode__(self):
        return self.name

class UserTrackedContent(models.Model):
    """
    Content types being tracked.
    """
    content_type = models.ForeignKey(ContentType)
    action = models.ForeignKey(UserAction)
    
    def __unicode__(self):
        return "%s::%s" % (self.content_type.model, self.action.name)
    
class UserHistory(models.Model):
    """
    Instance of UserAction denoting a single user action.
    """
    action = models.ForeignKey(UserAction)
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField()
    object = generic.GenericForeignKey()
    user = models.ForeignKey(User)
    
    date_created = CreationDateTimeField()
    
    objects = UserHistoryManager()
    
    def __unicode__(self):
        return "%s action on %s of %s" % (self.action.name,  self.object_id,  self.content_type.model)