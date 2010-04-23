from django.db import models
from django.contrib.auth.models import User

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django_multivoting.models import Vote
import django_qa.settings as settings
from django.core.exceptions import ObjectDoesNotExist
import django_contenthistory.signals as signals
from django_common.managers import LimitingManager, BaseObjectsManager
from django_moderation.managers import HiddenContentManager
from django_qa.signals import answer_accepted

class QuestionManager(BaseObjectsManager, LimitingManager, HiddenContentManager):
    def accept_answer(self, answer):
        """
        Accepts an @answer as the correct answer to a question.  Each question
        can only have max 1 accepted answer.
        """
        if not self.get_accepted_answer(answer.question):
            answer.accepted = True
            answer.save()
            answer_accepted.send(sender = Answer, instance = answer)
        else:
            answer = None
        return answer
    
    def get_accepted_answer(self, question):
        """
        Returns the accepted answer for target @question if
        it has one, otherwise return None.
        """
        try:
            answer = Answer.objects.get(question = question,
                                        accepted = True)
        except ObjectDoesNotExist:
            answer = None
        return answer
    
    def get_answers(self, question, option = 'highest_rated'):
        """
        Returns a QuerySet of answers associated with target @question
        sorted by @option.
        """
        if option == 'most_recent':
            answers = Answer.objects.get_sorted_objects(option).filter(question = question)
        elif option == 'most_discussed':
            answers = Answer.objects.get_sorted_objects(option).filter(question = question)
        elif option == 'highest_rated':
            answers = Answer.objects.get_sorted_objects(option).filter(question = question)
        return answers
    
    def add(self, user, data):
        """
        Create a new question owned by @user based on 
        @data.
        """
        if self.can_add(user):    
            name = data.get('title', None)
            body = data.get('question', None)
              
            question = self.model(name = name, question = body, user = user)
            question.save()
            
            signals.edit.send(self.model, original=None, current=question, editor=user)
        else:
            question = None
        return question
    
    def edit(self, question, user, data):
        """
        Modifies target @question with new @data.  Sends edit
        signal.
        """
        name = data.get('title', None)
        body = data.get('question', None)
        
        original = self.model.objects.get(id = question.id)
        question.name = name
        question.question = body
        question.save()
        signals.edit.send(sender=self.model, original=original, current=question, editor=user)
        return question
    
class AnswerManager(BaseObjectsManager):
    def answer_question(self, answer, question, user):
        """
        Answers target @question with @answer.
        """
        try:
            answer = self.model.objects.get(user = user, question = question)
        except ObjectDoesNotExist:
            answer = self.model(answer = answer, question = question, user = user)
            answer.save()
        
        signals.edit.send(sender=self.model, original=None, current=answer, editor=user)
        return answer
    
    def edit(self, answer, user, data):
        """
        Modifies an @answer with new @data.  Sends edit signal.
        """
        ans = data.get('answer', None)
        
        original = self.model.objects.get(id = answer.id)
        answer.answer = ans
        answer.save()
        
        signals.edit.send(sender=self.model, original=original, current=answer, editor=user)
        return answer

class Question(models.Model):
    name = models.TextField()
    question = models.TextField()
    slug = models.SlugField()
    user = models.ForeignKey(User)
    
    date_created = CreationDateTimeField()
    date_modified = ModificationDateTimeField()
    
    objects = QuestionManager()
    
    def __unicode__(self):
        return self.title
    
class Answer(models.Model):
    answer = models.TextField()
    accepted = models.BooleanField(default = False)
    question = models.ForeignKey(Question,  related_name = 'answers')
    user = models.ForeignKey(User)
    
    date_created = CreationDateTimeField()
    date_modified = ModificationDateTimeField()
    
    objects = AnswerManager()
    
    @property
    def name(self):
        return self.question.name