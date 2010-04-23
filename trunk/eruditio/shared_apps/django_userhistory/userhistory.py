from django_userhistory.models import UserTrackedContent

class UserHistoryRegistry(object):
    """
    Registry for UserHistory handlers.  Necessary so that only one
    receiver is registered for each UserTrackedContent object.
    """
    def __init__(self):
        self._registry = {}
        self._handlers = {}
        user_tracked_contents = UserTrackedContent.objects.all()
        for content in user_tracked_contents:
            self.register(content.content_type, content.action)
    
    def get_handler(self, content_name):
        """
        Attempt to get a handler for target content type, based
        on the following naming convention.
        
        content_type.model_class()._meta.db_table as StudlyCaps + Handler
        """
        import django_userhistory.handlers as handlers
        
        def to_studly(x):
            return "".join([token.capitalize() for token in x.split("_")])
                            
        handler_class = getattr(handlers, 
                                "%sHandler" % (to_studly(content_name)), 
                                handlers.BaseUserHistoryHandler)
        return handler_class
    
    def register(self, content_type, action):
        """
        Registers a handler from django_userhistory.handlers with the target
        content type.
        """
        content_name = content_type.model_class()._meta.db_table
        if not content_name in self._registry.keys():
            HandlerClass = self.get_handler(content_name)
            handler = HandlerClass(content_type, action)
            self._registry[content_name] = content_type
            self._handlers[content_name] = handler
            
user_history_registry = UserHistoryRegistry()