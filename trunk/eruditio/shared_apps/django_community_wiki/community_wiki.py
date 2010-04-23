"""
Exposes a community_wiki object which can be used to clean
up content on the site by becoming the owner of content
that is to be deleted.
"""

from django.contrib.auth.models import User
from django_moderation.models import ContentFlag, CommunityWikiContent
from django_multivoting.models import Vote
import django_community_wiki.config as config
from django.db.models.signals import post_save
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

class CommunityWiki(object):
    """
    Community wiki object for handling content cleanup such as deletion and
    community wiki ownership.  Assumes that there is an user named community_wiki.
    """
    def __init__(self):
        try:
            self.user = User.objects.get(username = 'community_wiki')
        except ObjectDoesNotExist:
            self.user = User.objects.create_user(username = 'community_wiki',
                                                 email = 'community_wiki@superusers.com')
            
        post_save.connect(self._vote_signal_callback, sender = Vote, weak = False)
        post_save.connect(self._flag_signal_callback, sender = ContentFlag, weak = False)
        
    def is_community_wiki_content(self, content_type):
        """
        Returns True if content_type is a CommunityWikiContent type else return False.
        """
        return content_type.id in [x.content_type.id for x in CommunityWikiContent.objects.all()]
    
    def check_votes(self, instance):
        """
        Checks to determine if the current vote has pushed the object
        above the COMMUNITY_WIKI_VOTE_LIMIT in which case the object
        will be owned by the community_wiki.
        """
        target_node = instance.content_object
        content_type = instance.content_type
        if self.is_community_wiki_content(content_type):
            up_votes = Vote.objects.votes_for_object(target_node, Vote.UP)
            popularity = Vote.objects.popularity(target_node)
            if up_votes >= config.COMMUNITY_WIKI_VOTE_LIMIT:
                self.own_content(target_node)
            if popularity <= config.COMMUNITY_WIKI_POPULARITY_LIMIT:
                self.delete_content(node)
            
    def check_flags(self, instance):
        """
        Checks to determine if the the delete flag has been associated
        with the object.  If so, then the object will become community
        wiki owned.
        """
        target_node = instance.content_object
        content_type = instance.content_type
        if self.is_community_wiki_content(content_type):
            if instance.flag.name == 'delete':
                self.own_content(target_node)
                
    def _vote_signal_callback(self, **kwargs):
        """
        Signal receiver for Vote.
        """
        instance = kwargs['instance']
        created = kwargs['created']
        if created:
            self.check_votes(instance)
    
    def _flag_signal_callback(self, **kwargs):
        """
        Signal receiver for ContentFlag.
        """
        instance = kwargs['instance']
        created = kwargs['created']
        if created:
            self.check_flags(instance)
            
    def own_content(self, node):
        """
        Take ownership of target content.
        """
        if not node.user.id == self.user.id:
            node.user = self.user
            node.save()
    
    def delete_content(self, node):
        """
        Delete target content by adding a delete flag to it.
        """
        self.own_content(node)
        if not ContentFlag.objects.has_flag(node, 'delete'):
            ContentFlag.objects.add_flag(node, 'delete')
community_wiki = CommunityWiki()