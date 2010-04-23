import django.http as http
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

import django_community.utils as community_utils
import django_qa.forms as forms
import django_qa.models as models
import django_utils.pagination as pagination
import django_utils.request_helpers as request_helpers
import django_community.decorators as community_decorators
from django_reputation.decorators import reputation_required
from django_metatagging.views import RetagAction
from django_moderation.views import FlagAction
from django_common.views import ListView, ContributeView, EditView
from django_tracking.models import View

qa = ListView(model = models.Question,
              per_page = 20,
              ordered = True,
              moderated = False,
              template = 'django_qa/questions.html')

ask = ContributeView(model = models.Question,
                                form_builder = forms.build_question_form,
                                redirect_url = 'qa-view-question',
                                template = 'django_qa/ask.html')

edit_question = EditView(model = models.Question,
                         form_builder = forms.build_question_form,
                         view_url = 'qa-view-question',
                         redirect_url = 'qa-view-question',
                         template = 'django_qa/edit_question.html')

edit_answer = EditView(model = models.Answer,
                         form_builder = forms.build_answer_form,
                         view_url = 'qa-view-answer',
                         redirect_url = 'qa-view-answer',
                         template = 'django_qa/edit_answer.html')

@community_decorators.user_required
def accept_answer(request,  answer_id):
    answer = models.Answer.objects.get(id = answer_id)
    question = answer.question
    status = models.Question.objects.accept_answer(answer)
    redirect_url = reverse('qa-view-question',  args=[question.id])
    return http.HttpResponseRedirect(redirect_url)

def view_question(request,  question_id):
    option = request.GET.get('option', 'highest_rated')
    
    page = request_helpers.get_page(request)
    user = request.user
    question = get_object_or_404(models.Question, id = question_id)
    question.accepted_answer = models.Question.objects.get_accepted_answer(question)
    AnswerForm = forms.build_answer_form()
    
    if user and request.POST:
        answer_form = AnswerForm(request.POST,  request.FILES)
        answer_form.question = question
        answer_form.user = user
        if answer_form.is_valid():
            answer = models.Answer.objects.answer_question(answer_form.cleaned_data['answer'], question, user)
    else:
        answer_form = AnswerForm()
    
    answers = models.Question.objects.get_answers(question, option)
    current_page, page_range = pagination.paginate_queryset(answers, 20, 5, page)
    
    View.objects.add(question, request_helpers.get_ip(request))
    
    return shortcuts.render_to_response(
                'django_qa/view.html', 
                {'question':question,  
                 'form':answer_form,  
                 'is_owner':question.user.id == user.id,
                 'current_page':current_page,
                 'page_range':page_range,
                 'sort':option}, 
                context_instance = RequestContext(request),
    )

def view_answer(request,  answer_id):
    answer = get_object_or_404(models.Answer,  id = answer_id)
    question = answer.question
    answer_url = "%s#answer_%s" % (reverse('qa-view-question',  args=[question.id]), str(answer.id))
    View.objects.add(question, request_helpers.get_ip(request))
    return http.HttpResponseRedirect(answer_url)

flag_question = FlagAction(models.Question, 
                           forms.build_flag_question_form, 
                           'django_qa/elements/question_flag_form.html', 
                           'qa-view-question')

retag_question = RetagAction(models.Question, 
                             forms.build_question_form, 
                             'shared/retag.html', 
                             'qa-view-question')

flag_answer = FlagAction(models.Answer, 
                         forms.build_flag_answer_form, 
                         'django_qa/elements/answer_flag_form.html', 
                         'qa-view-answer')