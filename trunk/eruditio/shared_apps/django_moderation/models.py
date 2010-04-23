from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django.core.exceptions import ObjectDoesNotExist

import django_moderation.config as config
from django_reputation.utils import has_permission
from django_reputation.models import Reputation
from django_moderation.exceptions import ContentFlagException, ContentApprovalException

class ContentApprovalManager(models.Manager):
    def queue(self, user, content_type = None):
        """
        Return the current instance in the moderation queue that is available
        to the user.
        """
        flag = ContentFlag.objects.get(name = ContentFlag.MODERATE_FLAG)
        where_clause = """((SELECT COUNT(*) FROM %(approval_table)s WHERE
                        %(approval_table)s.user_id = %(user_id)s AND
                        %(approval_table)s.content_type_id = %(flag_table)s.content_type_id AND
                        %(approval_table)s.object_id = %(flag_table)s.object_id) = 0)
                        """ % {'approval_table':ContentApprovalVote._meta.db_table,
                               'user_id':str(user.id),
                               'flag_table':ContentFlagInstance._meta.db_table}
        try:
            instance = ContentFlag.objects.objects_with_flag(flag, content_type).extra(where = [where_clause])[0]
        except IndexError:
            instance = None
        return instance
    
    def vote(self, object, user, mode):
        """
        Add an accept, pass or reject vote to an object that is currently under moderation.
        """
        if self.can_vote(object, user) and self.can_moderate(object):
            content_type_object, object_id = ContentType.objects.get_for_model(object.__class__), object.id
            try:
                vote = super(ContentApprovalManager, self).get(content_type = content_type_object, 
                                                               object_id = object_id, 
                                                               user = user)
                vote.mode = mode
                vote.save()
            except ObjectDoesNotExist:
                weight = self.weight_for_vote(mode, user)
                vote = self.model(content_type = content_type_object, 
                                  object_id = object_id, 
                                  user = user,
                                  weight = weight, 
                                  mode = mode)
                vote.save()
                self.check_threshold(object)
            return True
        else:
            return False
    
    def weight_for_vote(self, mode, user):
        """
        Method that returns the weight of a vote based on user reputation.
        """
        if mode == ContentApprovalVote.ACCEPT:
            return Reputation.objects.reputation_for_user(user).reputation
        elif mode == ContentApprovalVote.REJECT:
            return -1 * Reputation.objects.reputation_for_user(user).reputation
        elif mode == ContentApprovalVote.PASS:
            return 0
        else:
            raise ContentApprovalException("invalid ContentApprovalFlag mode specified: %s" % (str(mode)))
        
    def can_vote(self, object, user):
        """
        Return True if the target user can cast votes to moderate content, else return False.
        """
        ANONYMOUS_APPROVAL_ENABLED = getattr(config, 'ANONYMOUS_APPROVAL_ENABLED', False)
        if (user.is_authenticated() or ANONYMOUS_APPROVAL_ENABLED) and \
            (has_permission(user, 'access_moderation_queue') or \
             has_permission(user, 'moderate_%s' % (object.__class__._meta.db_table))):
            content_type_object, object_id = ContentType.objects.get_for_model(object.__class__), object.id
            vote_count = super(ContentApprovalManager, self).filter(content_type = content_type_object, 
                                                                    object_id = object_id, 
                                                                    user = user).count()
            if vote_count >= 1:
                return False
            else:
                return True
        else:
            return False
    
    def can_moderate(self, object):
        """
        Determine if the target object is of a content type associated
        with a ModeratedContent object.
        """
        content_type_object, object_id = ContentType.objects.get_for_model(object.__class__), object.id
        return bool(ModeratedContent.objects.filter(content_type = content_type_object))

    def approve(self, object):
        """
        Associate an ACCEPT_FLAG with the target object denoting
        that it has passed moderation successfully.
        
        @param object
        """
        status = ContentFlag.objects.add_flag(object, ContentFlag.ACCEPT_FLAG)
        return status
    
    def reject(self, object):
        """
        Associate a REJECT_FLAG with the target object denoting that
        is has failed the moderation process.
        
        @param object
        """
        status = ContentFlag.objects.add_flag(object, ContentFlag.REJECT_FLAG)
        return status
    
    def queue_for_moderation(self, object):
        """
        Queue an object for moderation by associating a MODERATION_FLAG.
        """
        
        status = ContentFlag.objects.add_flag(object, ContentFlag.MODERATE_FLAG)
        return status
    
    def check_threshold(self, object):
        """
        Check the weight thresholds on the associated ModeratedContent objects to determine
        if an object should be accepted or rejected.
        """
        content_type_object, object_id = ContentType.objects.get_for_model(object.__class__), object.id
        total_weight = sum([x.weight for x in self.model.objects.filter(content_type = content_type_object, 
                                                                        object_id = object_id)])
        moderation_object = ModeratedContent.objects.get(content_type = content_type_object)
        
        if total_weight >= moderation_object.accept_threshold:
            self.approve(object)
            return 1
        elif total_weight <= moderation_object.reject_threshold:
            self.reject(object)
            return -1
        else:
            return 0
    
class ContentFlagManager(models.Manager):
    def objects_with_flag(self, flag, content_type = None):
        """
        Return a queryset of objects that have the target flag associated with them.
        """
        content_flag_object = self.get_flag_object(flag)
        if content_type:
            content_type_object = ContentType.objects.get(id = int(content_type))
            instances = ContentFlagInstance.objects.filter(content_type = content_type_object,
                                                           flag = content_flag_object)
        else:
            instances = ContentFlagInstance.objects.filter(flag = content_flag_object)
        return instances
    
    def flags_for_object(self, object):
        """
        Return all the flags associated to the target object.
        
        @param object: django models.Model with an associated ContentType
        @rtype: C{list} of L{ContentFlagInstance}
        """
        content_type_object, object_id = ContentType.objects.get_for_model(object.__class__), object.id
        return ContentFlagInstance.objects.filter(content_type = content_type_object, 
                                                  object_id = object_id)
    
    def has_flag(self, target_object, flag):
        """
        Returns True if the target object has been flagged with flag else return False.
        """
        content_flag_object = self.get_flag_object(flag)
        content_type_object, object_id = ContentType.objects.get_for_model(target_object.__class__), target_object.id
        return ContentFlagInstance.objects.filter(content_type = content_type_object, 
                                                  object_id = object_id,
                                                  flag = content_flag_object)
        
    def add_flag(self, object, flag):
        """
        Associate a flag with an object.  Also checks to see if the added flag is part of
        an exclusive set, if so remove all other flags from that exclusive set.
        """
        content_flag_object = self.get_flag_object(flag)
        content_type_object, object_id = ContentType.objects.get_for_model(object.__class__), object.id
        
        try:
            content_flag_instance = ContentFlagInstance.objects.get(content_type = content_type_object, 
                                                                    object_id = object_id,
                                                                    flag = content_flag_object)
        except ObjectDoesNotExist:
            content_flag_instance = ContentFlagInstance(content_type = content_type_object, 
                                                        object_id = object_id,
                                                        flag = content_flag_object)
            content_flag_instance.save()
            self.exclude_for_set(object, content_flag_object)
        return content_flag_instance
    
    def remove_flag(self, object, flag):
        """
        Remove a flag from an object.
        """
        content_flag_object = self.get_flag_object(flag)
        content_type_object, object_id = ContentType.objects.get_for_model(object.__class__), object.id
        
        try:
            content_flag_instance = ContentFlagInstance.objects.get(content_type = content_type_object, 
                                                                    object_id = object_id,
                                                                    flag = content_flag_object)
            content_flag_instance.delete()
        except ObjectDoesNotExist:
            content_flag_instance = None
        return content_flag_instance
            
    def exclude_for_set(self, object, flag):
        """
        Check for flags that are in exclusive sets and remove the the existing
        flags which are in the same set as flag with exclusive = True
        
        @param object: django models.Model with an associated ContentType
        @param flag: ContentFlag object
        @rtype: C{list} of L{ContentFlagInstance}
        """
        flags_removed = []
        content_flag_sets = [x.set for x in ContentFlagSetMember.objects.filter(flag = flag)]
        for set in content_flag_sets:
            if set.exclusive:
                current_flags = self.flags_for_object(object)
                for current_flag in current_flags:
                    if not current_flag.flag.name == flag.name:
                        content_flag_instance = self.remove_flag(object, current_flag.flag)
                        flags_removed.append(content_flag_instance)
        return flags_removed
    
    def get_flag_object(self, flag):
        """
        Helper method for getting a ContentFlag agnostic to str and ContentFlag classes.
        """
        if flag.__class__ == ContentFlag:
            content_flag_object = flag
        else:
            try:
                content_flag_object = self.model.objects.get(name = str(flag))
            except Exception, e:
                content_flag_object = None
                raise ContentFlagException("ContentFlag %s does not exist" % (str(flag)))
        return content_flag_object
    
class ContentFlagVoteManager(models.Manager):
    def add_vote(self, content_type_id, object_id, flag, reason, details, user):
        """
        Add a ContentFlagVote.
        """
        try:
            content_type_object = ContentType.objects.get(id = content_type_id)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist("invalid content_type specified")
        
        try:
            flag_vote = self.model.objects.get(content_type = content_type_object, 
                                               object_id = object_id, 
                                               user = user)
        except ObjectDoesNotExist:
            try:
                content_flag = ContentFlag.objects.get(name = flag)
                reason = Reason.objects.get(name = reason)
                flag_vote = self.model(content_type = content_type_object, 
                                            object_id = object_id, 
                                            user = user, 
                                            reason = reason,
                                            flag = content_flag,
                                            additional_info = details,
                                            weight = config.DEFAULT_FLAG_VOTE_WEIGHT)
                flag_vote.save()
                self.check_flag_threshold(content_type_object.id, object_id, flag)
            except ObjectDoesNotExist:
                raise ObjectDoesNotExist("invalid reason and/or flag provided")
        return flag_vote
    
    def check_flag_threshold(self, content_type, object_id, flag):
        """
        Determine if the current flag vote hit the FLAG_VOTE_THRESHOLD, 
        if so associate the flag with the current object.
        """
        content_type_object = ContentType.objects.get(id = content_type)
        target_object = content_type_object.model_class().objects.get(id = object_id)
        flag_object = ContentFlag.objects.get_flag_object(flag)
        flag_votes = self.model.objects.filter(content_type = content_type_object, 
                                               object_id = object_id,
                                               flag = flag_object)
        if flag_votes.count() >= config.FLAG_VOTE_THRESHOLD:
            ContentFlag.objects.add_flag(target_object, flag)
        
    def get_vote_for_content(self, content, user):
        """
        If the target user has flagged the the target object, return the
        ContentFlagVote, else return None.
        """
        content_type_object = ContentType.objects.get_for_model(content)
        object_id = content.id
        
        try:
            flag_vote = self.model.objects.get(content_type = content_type_object, object_id = object_id, user = user)
        except ObjectDoesNotExist:
            flag_vote = None
        
        return flag_vote
    
class ContentFlagSet(models.Model):
    """
    A set of related ContentFlags.
    """
    name = models.CharField(max_length = 75, unique = True)
    exclusive = models.BooleanField(default = True)
    active = models.BooleanField(default = True)
    description = models.TextField()
    
    def __unicode__(self):
        return self.name
    
class ContentFlag(models.Model):
    """
    A flag that can be associated with an object.
    """
    ACCEPT_FLAG = 'content_accept'
    REJECT_FLAG = 'content_reject'
    MODERATE_FLAG = 'content_in_moderation'
    HIDDEN_FLAG = 'delete'
    
    name = models.CharField(max_length = 75, unique = True)
    active = models.BooleanField(default = True)
    description = models.TextField()
    
    objects = ContentFlagManager()
    
    def __unicode__(self):
        return self.name
    
class ContentFlagSetMember(models.Model):
    """
    M2M between ContentFlag and ContentFlagSet.
    """
    set = models.ForeignKey(ContentFlagSet)
    flag = models.ForeignKey(ContentFlag)
    
    def __unicode__(self):
        return "%s::%s" % (self.set.__unicode__(), self.flag.__unicode__())
    
class Reason(models.Model):
    """
    Reason for submitting a ContentFlagVote
    """
    name = models.CharField(max_length = 75, unique = True)
    description = models.TextField()
    
    def __unicode__(self):
        return "%s-----%s" % (self.name, self.description)
    
class ContentFlagInstance(models.Model):
    """
    M2M table representing instances of ContentFlags associated with objects.
    """
    flag = models.ForeignKey(ContentFlag)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    
    date_created = CreationDateTimeField()
    date_modified = ModificationDateTimeField()
    
class ContentFlagVote(models.Model):
    """
    Represents a users vote to flag a piece of content with a particular ContentFlag.
    """
    additional_info = models.TextField(default = '')
    reason = models.ForeignKey(Reason)
    flag = models.ForeignKey(ContentFlag)
    user = models.ForeignKey(User)
    weight = models.IntegerField(default = 1)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    
    date_created = CreationDateTimeField()
    date_modified = ModificationDateTimeField()
    
    objects = ContentFlagVoteManager()

class ModeratedContent(models.Model):
    """
    Content that has to undergo moderation before it can be shown
    to the public.
    """
    content_type = models.ForeignKey(ContentType)
    
    accept_threshold = models.IntegerField(default = 0)
    reject_threshold = models.IntegerField(default = 0)
    
    def __unicode__(self):
        return str(self.content_type.model)
    
class ContentApprovalVote(models.Model):
    """
    Represents a moderation vote by a moderator.  Can be
    accept, reject or pass.
    """

    ACCEPT, REJECT, PASS = 'accept', 'reject', 'pass'
    VOTE_CHOICES = (('accept', 'accept'), ('pass', 'pass'), ('reject', 'reject'),)
    
    mode = models.CharField(max_length = 75, choices = VOTE_CHOICES)
    user = models.ForeignKey(User)
    weight = models.IntegerField()
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    
    date_created = CreationDateTimeField()
    date_modified = ModificationDateTimeField()
    
    objects = ContentApprovalManager()

class CommunityWikiContent(models.Model):
    """
    Content that can be owned by the community_wiki if certain
    conditions are met.
    """
    content_type = models.ForeignKey(ContentType)
    
    def __unicode__(self):
        return str(self.content_type.model)