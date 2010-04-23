from django_contenthistory.models import TrackedContent
import django_contenthistory.handlers as handlers

class ContentHistory(object):
    """
    Registry of handlers for TrackedContent content types.
    """
    def __init__(self):
        self._registry = {}
        self._handlers = {}
        tracked_contents = TrackedContent.objects.all()
        for content in tracked_contents:
            self.register(content.content_type)
    
    def get_handler(self, content_type):
        """
        Returns a handler class based on StudlyCaps notation of
        content_type.app_label + content_type.model + HistoryHandler.
        Defaults to BaseHistoryHandler.
        """
        handler_name = "%s%s%s" % (content_type.app_label.capitalize(), 
                                    content_type.model.capitalize(), 
                                    "HistoryHandler")
        handler_class = getattr(handlers, handler_name, handlers.BaseHistoryHandler)
        return handler_class
    
    def register(self, content_type):
        """
        Registers a callable handler instance in the registry.
        """
        content_name = "%s_%s" % (content_type.app_label, content_type.model)
        if not content_name in self._registry.keys():
            HandlerClass = self.get_handler(content_type)
            handler = HandlerClass(content_type)
            self._handlers[content_name] = handler
            self._registry[content_name] = content_type
            
content_history = ContentHistory()