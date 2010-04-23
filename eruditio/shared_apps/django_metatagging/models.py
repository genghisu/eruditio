from django.db import models
from django.contrib.contenttypes.models import ContentType

from tagging.models import Tag

class ReservedTagSet(models.Model):
    """
    Set of ReservedTag objects which are mutually exclusive.
    """
    name = models.CharField(max_length = 75, unique = True)
    
class ReservedTag(models.Model):
    """
    A reserved tag which cannot be used by standard users
    to tag objects and has some special administrative use.
    """
    name = models.CharField(max_length = 75, unique = True)
    description = models.TextField()
    set = models.ForeignKey(ReservedTagSet)

class AgnosticTags(models.Model):
    """
    Tags which mean the same thing.  Used to make tag entry agnostic
    to spelling errors and synonyms.
    """
    primary = models.ForeignKey(Tag, related_name = 'primary')
    secondary = models.ForeignKey(Tag, related_name = 'secondary')