from django.db import models
from django.contrib.auth.models import User

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

class BadgeManager(models.Manager):
    """
    Custom manager for the Badge model.
    
    The methods defined here provide shortcuts for badge creation,
    and badge retrieval.
    """
    def create_badge(self, badge, user, content_type, object_id):
        """
        Creates a BadgeInstance object.
        """
        badge_instance = BadgeInstance(user = user,
                                       badge = badge,
                                       content_type = content_type,
                                       object_id = object_id)
        badge_instance.save()
        return badge_instance
    
    def distinct_badges_for_user_with_count(self, user):
        """
        Returns a QuerySet of distinct Badge objects that
        the user has obtained.
        """
        values = {}
        values['badge_instance_table'] = BadgeInstance._meta.db_table
        values['badge_table'] = self.model._meta.db_table
        values['user_id'] = user.id
        
        where_clause = """((SELECT COUNT(*) FROM %(badge_instance_table)s WHERE
                            %(badge_instance_table)s.user_id = %(user_id)s AND
                            %(badge_instance_table)s.badge_id = %(badge_table)s.id) > 0)""" % values
        
        badges = self.model.objects.all().extra(where = [where_clause])
        for badge in badges:
            badge.count = BadgeInstance.objects.filter(badge = badge, user = user).count()
            
        return badges
        
    def badges_for_user(self, user):
        """
        Return all BadgeInstance objects that have been awarded
        to the user.
        """
        return BadgeInstance.objects.filter(user = user)
    
    def badges_with_count(self):
        """
        Return all Badge objects with the associated number
        of BadgeInstance objects associated with each Badge.
        """
        badges = self.model.objects.all().order_by('name')
        for badge in badges:
            badge.count = BadgeInstance.objects.filter(badge = badge).count()
        return badges
    
    def users_with_badge(self, badge):
        """
        Returns a QuerySet of all users who have been awarded at least
        one instance of a Badge.
        """
        values = {}
        values['badge_table'] = BadgeInstance._meta.db_table
        values['user_table'] = User._meta.db_table
        values['badge_id'] = badge.id
        
        where_clause = """((SELECT COUNT(*) FROM %(badge_table)s WHERE
                            %(badge_table)s.user_id = %(user_table)s.id AND
                            %(badge_table)s.badge_id = %(badge_id)s) > 0)""" % values
        users = User.objects.all().extra(where = [where_clause])
        return users
                            
class Badge(models.Model):
    """
    Definition of a badge that can be awarded when a user 
    fulfills a set of defined conditions.
    """
    LEVELS = (
        ("Bronze", "Bronze"),
        ("Silver", "Silver"),
        ("Gold", "Gold"),             
        )
    
    name = models.CharField(max_length = 75)
    description = models.TextField(default = '')
    level = models.CharField(max_length = 75, choices = LEVELS)
    
    objects = BadgeManager()
    
    def __unicode__(self):
        return "%s (%s)" % (str(self.name), str(self.level))

class BadgeInstance(models.Model):
    """
    Represents an instance of a Badge that has been
    awarded to an user.
    """
    user = models.ForeignKey(User)
    badge = models.ForeignKey(Badge)
    
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = generic.GenericForeignKey()
    
    def __unicode__(self):
        return "%s::%s" % (self.badge.name, self.user.username)