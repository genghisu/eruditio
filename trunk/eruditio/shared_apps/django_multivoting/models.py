from django.db import models, connection
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User
import django_multivoting.config as config
from django.conf import settings
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField

class VoteManager(models.Manager):
    def votes_for_user(self, user):
        """
        Returns the number of votes an @user has cast.
        """
        return super(VoteManager, self).get_query_set().filter(user = user).count()
    
    def votes_for_object(self, object, vote_mode):
        """
        Returns the number of votes of a target @mode that has been
        cast on an @object.
        """
        content_type_object, object_id = ContentType.objects.get_for_model(object.__class__), object.id
        return super(VoteManager, self).get_query_set().filter(content_type = content_type_object, object_id = object_id, mode = vote_mode).count()
        
    def popularity(self, object):
        """
        Returns the popularity of an @object.
        """
        content_type_object, object_id = ContentType.objects.get_for_model(object.__class__), object.id
        
        try:
            object_popularity = Popularity.objects.get(content_type = content_type_object, object_id = object.id)
        except ObjectDoesNotExist:
            object_popularity = Popularity(content_type = content_type_object, object_id = object.id)
            object_popularity.save()
        return object_popularity
    
    def handle_vote(self, user, object, vote_mode):
        """
        Casts a vote of @vote_mode targeted at @object by @user.  Checks for
        vote conditions and returns True if the vote is cast successfully.
        If a previous vote has already been registered with target @object
        by @user, then the previous vote will be reversed if the vote_mode
        is not the same.
        """
        content_type_object, object_id = ContentType.objects.get_for_model(object.__class__), object.id
        MAX_VOTES = getattr(config, 'MAX_VOTES_PER_OBJECT')
        ANONYMOUS_VOTING_ENABLED = getattr(config, 'ANONYMOUS_VOTING_ENABLED', False)
        CAN_OWNER_VOTE = getattr(config, 'CAN_OWNER_VOTE', False)
        
        vote_count = super(VoteManager, self).get_query_set().filter(content_type = content_type_object, object_id = object_id, user = user).count()
        if (user.is_authenticated() or ANONYMOUS_VOTING_ENABLED) and (not user == getattr(object, 'user', None) or CAN_OWNER_VOTE):
            if vote_count < MAX_VOTES:
                new_vote = Vote(content_type = content_type_object, object_id = object_id, mode = vote_mode, user = user)
                new_vote.save()
                confirmation = True
            else:
                same_votes = super(VoteManager, self).filter(content_type = content_type_object, object_id = object_id, mode = vote_mode, user = user)
                reverse_votes = super(VoteManager, self).filter(content_type = content_type_object, object_id = object_id, user = user).exclude(mode = vote_mode)
                if same_votes.count() >= MAX_VOTES:
                    confirmation = False
                else:
                    target_reverse_vote = reverse_votes[0]
                    target_reverse_vote.mode = vote_mode
                    target_reverse_vote.save()
                    confirmation = True
        else:
            confirmation = False
        
        if confirmation == True:
            vote_count = super(VoteManager, self).get_query_set().filter(content_type = content_type_object, object_id = object_id, mode = vote_mode).count()
             
        self.update_popularity(object)
        return confirmation
    
    def update_popularity(self, object):
        """
        Calculates the current popularity of target @object by subtracting
        the number of down votes from the number of up votes that @object
        has.
        """
        content_type_object, object_id = ContentType.objects.get_for_model(object.__class__), object.id
        popularity = self.popularity(object)
        popularity.popularity = super(VoteManager, self).filter(content_type = content_type_object, object_id = object_id, mode = 'up').count() - \
                                super(VoteManager, self).filter(content_type = content_type_object, object_id = object_id, mode = 'down').count()
        popularity.save()
        return popularity
    
    def most_popular_objects(self, model, count = None, filters = {}):
        """
        Return a QuerySet of the most popular objects of a given @model
        returning a max of @count objects with additional filters 
        specified in @filters ordered by descending popularity.
        """
        model_content_type = ContentType.objects.get_for_model(model)
        model_table = "%s_%s" % (model_content_type.app_label,  model_content_type.model)
        
        popularity_content_type = ContentType.objects.get_for_model(Popularity)
        popularity_table = "%s_%s" % (popularity_content_type.app_label, popularity_content_type.model)
        
        select_clause = {'popularity' : 'SELECT popularity FROM %s WHERE %s.content_type_id = %s AND %s.object_id = %s.id' % \
                         (popularity_table, popularity_table, str(model_content_type.id), popularity_table, model_table)}
        order_clause = "-popularity"
        objects = model.objects.all()
        for filter in filters.items():
            objects.query.add_filter(filter)
        objects = objects.extra(select = select_clause).extra(order_by = [order_clause])
        if count:
            objects = objects[0:count]
        return objects
        
    def most_active_objects(self, model, date, count = None):
        """
        Returns a QuerySet of @count objects of @model that have
        the most number of votes casted during the period of 
        date to now ordered by descending number of votes.
        """
        model_content_type = ContentType.objects.get_for_model(model)
        model_table = "%s_%s" % (model_content_type.app_label,  model_content_type.model)
        
        vote_content_type = ContentType.objects.get_for_model(Vote)
        vote_table = "%s_%s" % (vote_content_type.app_label, vote_content_type.model)
        
        select_clause = {'votes' : 'SELECT COUNT(*) FROM %s WHERE %s.content_type_id = %s AND %s.object_id = %s.id AND %s.date_created > %s' % \
                         (vote_table, vote_table, str(model_content_type.id), vote_table, model_table, vote_table, date)}
        order_clause = "-votes"
        objects = model.objects.all().extra(select = select_clause, order_by = [order_clause])
        if count:
            objects = objects[0:count]
        return objects
    
    def voted_objects_by_user(self, user, model):
        """
        Returns a QuerySet of all objects that target @user
        has casted votes on filtered by @model.
        """
        model_content_type = ContentType.objects.get_for_model(model)
        
        where_clause = ["""(SELECT COUNT(*) FROM %(vote_table)s
                        WHERE %(vote_table)s.content_type_id = %(model_content_type_id)s
                        AND %(vote_table)s.object_id = %(model_table)s.id
                        AND %(vote_table)s.user_id = %(user_id)s) > 0 """ % {
                            'vote_table':connection.ops.quote_name(self.model._meta.db_table),
                            'model_table':connection.ops.quote_name(model._meta.db_table),
                            'model_content_type_id':model_content_type.id,
                            'user_id':user.id
                        }]
        objects = model.objects.all().extra(where = where_clause)
        return objects
    
class Vote(models.Model):
    UP = 'up'
    DOWN = 'down'
    VOTE_MODES = ((UP, UP), (DOWN, DOWN))
    
    mode = models.CharField(choices = VOTE_MODES, max_length = 50)
    user = models.ForeignKey(User)
    date_created = CreationDateTimeField()
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    
    objects = VoteManager()

class Popularity(models.Model):
    popularity = models.IntegerField(default = 0)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()