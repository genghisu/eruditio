import datetime
from haystack.indexes import *
from haystack import site
from applications.models import App

class AppIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    
    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return App.objects.all()

site.register(App, AppIndex)
