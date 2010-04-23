import datetime
from haystack.indexes import *
from haystack import site
from code.models import Code

class CodeIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    
    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Code.objects.all()

site.register(Code, CodeIndex)
