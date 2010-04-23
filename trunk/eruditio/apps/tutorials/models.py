import datetime

from django.db import models
from django.conf import settings

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django.contrib.auth.models import User
from code.models import Code
import django_contenthistory.signals as signals
from django_common.managers import LimitingManager, BaseObjectsManager
from django_moderation.managers import HiddenContentManager

class TutorialManager(BaseObjectsManager, LimitingManager, HiddenContentManager):
    def add(self, user, data):
        if self.can_add(user):
            name = data.get('name', None)
            description = data.get('description', None)
            url = data.get('url', None)
            
            tutorial = self.model(name = name, description = description, url = url, user = user)
            tutorial.save()
            
            signals.edit.send(sender=self.model, original=None, current=tutorial, editor=user)
        else:
            tutorial = None
        return tutorial
        
    def edit(self, tutorial, user, data):
        name = data.get('name', None)
        description = data.get('description', None)
        url = data.get('url', None)
        
        original = self.model.objects.get(id = tutorial.id)
        tutorial.name = name
        tutorial.description = description
        tutorial.url = url
        tutorial.save()
        
        signals.edit.send(sender=self.model, original=original, current=tutorial, editor=user)
        return tutorial
    
class Tutorial(models.Model):
    name = models.CharField(max_length = 75)
    description = models.TextField()
    url = models.URLField()
    user = models.ForeignKey(User)
    
    local = models.BooleanField(default = False)
    details = models.TextField(default='')
    
    date_created = CreationDateTimeField()
    date_modified = ModificationDateTimeField()
    
    objects = TutorialManager()