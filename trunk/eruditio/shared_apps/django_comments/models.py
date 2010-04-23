from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django_common.managers import LimitingManager, BaseObjectsManager
import django_comments.config as settings

class CommentManager(BaseObjectsManager, LimitingManager):
    """'
    Custom manager for comments.
    
    Allows for comment creation and also contains shortcuts
    for retrieving useful sets of comments.
    """
    def add_comment(self, user, object, comment, parent = None):
        """
        Creates a new comment attached to @object created by @user.
        """
        if self.can_add(user, settings.MAX_COMMENTS_PER_DAY):
            object_content_type = ContentType.objects.get_for_model(object.__class__)
            new_comment = self.model(content = comment, 
                                     content_type = object_content_type, 
                                     object_id = object.id, 
                                     user = user,
                                     parent = parent)
            new_comment.save()
        else:
            new_comment = None
        return new_comment
    
    def edit_comment(self, comment, new_content):
        """
        Modifies a comment's content changing it to new_content.
        """
        comment.content = new_content
        comment.save()
        
    def comments_for_object(self, object, option = 'most_recent'):
        """
        Returns all the comments associated with @object sorting it by @option.
        """
        object_content_type = ContentType.objects.get_for_model(object.__class__)
        return self.get_sorted_objects(option).filter(object_id = object.id, content_type = object_content_type)
    
    def comments_by_user(self, user):
        """
        Returns all the comments that were posted by @user.
        """
        return self.model.objects.filter(user = user)
    
class Comment(models.Model):
    """
    Comment model which allows for comment replies through the parent
    field.  Can be attached to any object through the use of the 
    content_types framework.
    """
    content = models.TextField()
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    user = models.ForeignKey(User)
    parent = models.ForeignKey('self', related_name = 'child_comments', null = True, blank = True)
    
    date_created = CreationDateTimeField()
    date_modified = ModificationDateTimeField()
    
    objects = CommentManager()