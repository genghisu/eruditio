"""
Badge registry which attempts to register each Badge with a corresponding Badge handler
in handlers.py.  This is similar to the admin autodiscover functionality which will
cause the registration of handlers to be handled once and once only each time the application
is initiated.
"""

from django_badges.models import Badge
from django.conf import settings

class BadgesRegistry(object):
    """
    A registry of django_badges.handlers that are associated at the startup of this
    site.  Attempts to associate a handler for each Badge object found within the
    database.
    """
    def __init__(self):
        self._registry = {}
        self._handlers = {}
        badges = Badge.objects.all()
        for badge in badges:
            self.register(badge.name)
    
    def get_handler(self, badge_name):
        """
        Finds a corresponding handler in handlers.py by modifying the name of the 
        badge.  Returns None if no corresponding class is found in handlers.py.
        """
        import django_badges.handlers as handlers

        handler_class = getattr(handlers, badge_name.replace(" ", ""), None)
        return handler_class
    
    def register(self, badge_name):
        """
        Attempts to register a handler class with a Badge object.
        """
        if not badge_name in self._registry.keys():
            HandlerClass = self.get_handler(badge_name)
            if HandlerClass:
                handler = HandlerClass()
            else:
                handler = None
            self._handlers[badge_name] = handler
            self._registry[badge_name] = badge_name
            
if not getattr(settings, 'TEST', False):
    badges_registry = BadgesRegistry()
else:
    badges_registry = None