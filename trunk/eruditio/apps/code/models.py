import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django.contrib.auth.models import User
from core.models import Django, Python
from django_common.managers import LimitingManager, BaseObjectsManager
from django_moderation.managers import ModeratedContentManager, HiddenContentManager
import django_contenthistory.signals as signals

class CodeManager(BaseObjectsManager, LimitingManager, HiddenContentManager):
    def add(self, user, data):
        if self.can_add(user):
            name = data.get('title', None)
            description = data.get('description', None)
            code_body = data.get('code', None)
            mode = data.get('mode', None)
                                       
            try:
                code_mode = CodeMode.objects.get(name = mode)
            except ObjectDoesNotExist:
                code_mode = None
                
            code = self.model(name = name, description = description, code = code_body, mode = code_mode, user = user)
            code.save()
            
            signals.edit.send(sender=self.model, original=None, current=code, editor=user)
        else:
            code = None
        return code

    def edit(self, code, user, data):
        name = data.get('title', code.name)
        description = data.get('description', code.description)
        code_body = data.get('code', code.code)
        mode = data.get('mode', code.mode)
        
        original = self.model.objects.get(id = code.id)
        try:
            code_mode = CodeMode.objects.get(name = mode)
        except ObjectDoesNotExist:
            code_mode = None
            
        code.name = name
        code.description = description
        code.code = code_body
        code.mode = code_mode
        code.save()
        
        signals.edit.send(sender=self.model, original=original, current=code, editor=user)
            
class CodeMode(models.Model):
    MODES = (('middleware', 'middleware'), 
             ('context processor', 'context processor'),
             ('template tag', 'template tag'),
             ('template filter', 'template filter'),
             ('form field', 'form field'),
             ('form widget', 'form widget'),
             ('db field', 'db field'),
             ('misc', 'misc'),
             )
             
    name = models.CharField(max_length = 75)
    description = models.TextField()
    
    def __unicode__(self):
        return self.name
    
class Code(models.Model):
    name = models.CharField(max_length = 75)
    description = models.TextField()
    code = models.TextField(default = '')
    mode = models.ForeignKey(CodeMode)
    user = models.ForeignKey(User)
    
    date_created = CreationDateTimeField()
    date_modified = ModificationDateTimeField()
    
    objects = CodeManager()

class CodePackage(models.Model):
    name = models.CharField(max_length = 75)
    description = models.TextField()
    user = models.ForeignKey(User)
    
    date_created = CreationDateTimeField()
    date_modified = ModificationDateTimeField()

class CodePackageItem(models.Model):
    code = models.ForeignKey(Code)
    package = models.ForeignKey(CodePackage)