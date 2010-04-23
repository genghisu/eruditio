from django_moderation.exceptions import ModerationException
from django_moderation.models import ContentFlag, ContentApprovalVote, ModeratedContent, CommunityWikiContent
from django.db.models.signals import post_save

class ModerationHandler(object):
    """
    Handler for adding new objects that need moderation to the
    moderation queue by associating a MODERATE_FLAG with the new
    object.
    """
    def __init__(self, content_type_object):
        self.model = content_type_object.model_class()
        self.name = self.model._meta.db_table
        post_save.connect(self._signal_callback, sender=self.model, weak = False)
    
    def _disconnect_signal(self):
        post_save.disconnect(self._signal_callback, self.model)
        
    def queue_for_moderation(self, object):
        """
        Puts the object in the moderation queue by associating a content_in_moderation flag
        with the object.
        """
        ContentApprovalVote.objects.queue_for_moderation(object)
    
    def _signal_callback(self, **kwargs):
        """
        Signal receiver.
        """
        object = kwargs['instance']
        created = kwargs['created']
        if created:
            self.queue_for_moderation(object)