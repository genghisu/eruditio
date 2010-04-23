import django_moderation.config as settings
from django_moderation.exceptions import ModerationException
from django_moderation.models import ContentFlag, ContentApprovalVote, ModeratedContent
from django_moderation.handlers import ModerationHandler

class Moderation(object):
    """
    Registry for associating ModerationHandler instances
    with ModeratedContent content types.
    """
    def __init__(self):
        self._registry = {}
        self._handlers = {}
        moderated_contents = ModeratedContent.objects.all()
        for content in moderated_contents:
            self.register(content.content_type)
    
    def unregister(self, content_type):
        content_name = content_type.model_class()._meta.db_table
        if self._registry.get(content_name, None):
            handler = self._handlers.get(content_name)
            handler._disconnect_signal()
            del self._registry[content_name]
            del self._handlers[content_name]
            
    def register(self, content_type):
        """
        Registers a ModerationHandler to receive the post_save signal
        from a ModeratedContent.content_type.
        """
        content_name = content_type.model_class()._meta.db_table
        if not content_name in self._registry.keys():
            handler = ModerationHandler(content_type)
            self._registry[content_name] = content_type
            self._handlers[content_name] = handler
            
moderation = Moderation()