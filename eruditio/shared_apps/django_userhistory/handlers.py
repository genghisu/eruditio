from django_userhistory.models import UserTrackedContent, UserHistory
from django.db.models.signals import post_save

class BaseUserHistoryHandler(object):
    """
    Default handler for registering post_save signal callbacks.
    Will add UserHistory objects if the sender is being created.
    """
    def __init__(self, content_type_object, action):
        self.model = content_type_object.model_class()
        self.name = self.model._meta.db_table
        self.action = action
        post_save.connect(self._signal_callback, sender=self.model, weak = False)
    
    def get_user(self, instance):
        return getattr(instance, 'user', None)
    
    def track_history(self, instance):
        user = self.get_user(instance)
        if user:
            UserHistory.objects.add_user_history(user, self.action, instance)
        
    def _signal_callback(self, **kwargs):
        instance = kwargs['instance']
        created = kwargs['created']
        if created:
            self.track_history(instance)

class DjangoContenthistoryModelhistoryHandler(BaseUserHistoryHandler):
    """
    Special cased handler to be used with django_contenthistory for tracking
    content edits.
    """
    def track_history(self, instance):
        user = self.get_user(instance)
        if not instance.created and user:
            UserHistory.objects.add_user_history(user, self.action, instance.content_object)