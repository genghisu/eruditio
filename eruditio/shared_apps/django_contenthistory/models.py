from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django_extensions.db.fields import CreationDateTimeField
from django.contrib.auth.models import User

class TrackedContent(models.Model):
    """
    Content types that are to be tracked through ModelHistory objects.
    """
    content_type = models.ForeignKey(ContentType)
    
    def __unicode__(self):
        return "%s::%s" % (self.content_type.app_label, self.content_type.model)
    
class ModelField(models.Model):
    """
    Denotes a field in target content type that is to be tracked. Allows for
    the exclusion of fields that are low priority.
    """
    TEXT = 'text'
    M2M = 'm2m'
    OWNER = 'owner'
    FIELDS = ((TEXT, TEXT), (M2M, M2M), (OWNER, OWNER))
    
    name = models.CharField(max_length = 75)
    mode = models.CharField(max_length = 75, choices = FIELDS)
    content = models.ForeignKey(TrackedContent)

class ModelHistoryManager(models.Manager):
    def add_history(self, content_type, object_id, data, editor, created):
        history = self.model(data = data,
                             content_type = content_type,
                             object_id = object_id,
                             user = editor, 
                             created = created)
        history.save()
        return history
    
    def edits_for_object(self, object):
        content_type_object = ContentType.objects.get_for_model(object.__class__)
        object_id = object.id
        return self.model.objects.filter(content_type = content_type_object, 
                                         object_id = object_id, 
                                         created = False).order_by('-date_created')
    
    def edits_for_user(self, user):
        return self.model.objects.filter(user = user, created = False)
    
class ModelHistory(models.Model):
    """
    An instance of a edit/create event on an object.  data is a
    serialized python dictionary as json through json.dumps.
    """
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = generic.GenericForeignKey()
    
    created = models.BooleanField(default = False)
    data = models.TextField()
    description = models.TextField(default = '')

    user = models.ForeignKey(User)
    date_created = CreationDateTimeField()
    
    objects = ModelHistoryManager()
    
    def __unicode__(self):
        return "%s:::%s" % (str(self.content_type), str(self.object_id))