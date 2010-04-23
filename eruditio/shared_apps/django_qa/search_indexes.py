import datetime
from haystack.indexes import *
from haystack import site
from django_qa.models import Question, Answer

class QuestionIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    
    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Question.objects.all()

class AnswerIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    
    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Answer.objects.all()
    
site.register(Question, QuestionIndex)
site.register(Answer, AnswerIndex)