import datetime
from haystack.indexes import *
from haystack import site
from tutorials.models import Tutorial

class TutorialIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    
    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Tutorial.objects.all()

site.register(Tutorial, TutorialIndex)