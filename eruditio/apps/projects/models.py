from django.db import models

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django.contrib.auth.models import User

class DjangoProject(models.Model):
    name = models.CharField(max_length = 75)
    description = models.TextField()
    url = models.URLField()
    user = models.ForeignKey(User)
    
    date_created = CreationDateTimeField()
    date_modified = ModificationDateTimeField()