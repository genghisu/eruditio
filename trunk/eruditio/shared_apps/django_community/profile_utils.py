"""
Function for marshalling profile information in its own separate module
due to import issues.
"""

import hashlib
import re

from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

import django_community.models as models
from django_multivoting.models import Vote
from django_qa.models import Question, Answer
from applications.models import App
from code.models import Code
from tutorials.models import Tutorial
from django_community.models import Favorite
from django_utils.pagination import paginate_queryset_ajax
from django_userhistory.models import UserHistory
from django_badges.models import Badge

def build_profile_information(user):
    """
    Returns a dictionary containing information relevant to an user's 
    profile.
    
    Override this function to add additional information to an user's 
    profile.
    """
    context = {}
    context['user'] = user
    
    up_votes = Vote.objects.filter(user = user,  mode = 'up').count()
    down_votes = Vote.objects.filter(user = user,  mode = 'down').count()
    context['up_votes'] = up_votes
    context['down_votes'] = down_votes
    
    contributed_questions = Question.objects.filter(user = user)
    contributed_apps = App.objects.filter(user = user)
    contributed_codes = Code.objects.filter(user = user)
    contributed_tutorials = Tutorial.objects.filter(user = user)
    contributed_answers = Answer.objects.filter(user = user)
    
    apps_page,  apps_page_range = \
        paginate_queryset_ajax(contributed_apps,  10,  5,  1,  'apps_page_',  
                               reverse('community-contributed-content',  args=[user.id,  ContentType.objects.get_for_model(App).id]))
    codes_page,  codes_page_range = \
        paginate_queryset_ajax(contributed_codes,  10,  5,  1,  'codes_page_', 
                                reverse('community-contributed-content',  args=[user.id,  ContentType.objects.get_for_model(Code).id]))
    tutorials_page,  tutorials_page_range = \
        paginate_queryset_ajax(contributed_tutorials,  10,  5,  1,  'tutorials_page_', 
                                reverse('community-contributed-content',  args=[user.id,  ContentType.objects.get_for_model(Tutorial).id]))
    questions_page,  questions_page_range = \
        paginate_queryset_ajax(contributed_questions,  10,  5,  1,  'questions_page_',
                                reverse('community-contributed-content',  args=[user.id,  ContentType.objects.get_for_model(Question).id]))
    answers_page,  answers_page_range = \
        paginate_queryset_ajax(contributed_answers,  10,  5,  1,  'answers_page_', 
                                reverse('community-contributed-content',  args=[user.id,  ContentType.objects.get_for_model(Answer).id]))
    
    favorite_content = Favorite.objects.filter(user = user).order_by('-date_created')
    favorites_page,  favorites_page_range = paginate_queryset_ajax(favorite_content,  10,  5,  1,  'favorites_page_',  
                               reverse('community-contributed-content',  args=[user.id,  ContentType.objects.get_for_model(Favorite).id]))
    
    user_history = UserHistory.objects.filter(user = user).order_by('-date_created')[0:30]
    badges = Badge.objects.distinct_badges_for_user_with_count(user)
    
    context['apps_page'],  context['apps_page_range']  = apps_page,  apps_page_range
    context['codes_page'], context['codes_page_range'] = codes_page,  codes_page_range
    context['tutorials_page'],  context['tutorials_page_range'] = tutorials_page,  tutorials_page_range
    context['questions_page'],  context['questions_page_range'] = questions_page,  questions_page_range
    context['answers_page'],  context['answers_page_range'] = answers_page,  answers_page_range
    context['favorites_page'],  context['favorites_page_range'] = favorites_page,  favorites_page_range
    context['user_history'] = user_history
    context['badges'] = badges
    
    return context