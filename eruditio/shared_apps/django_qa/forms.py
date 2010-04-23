import django.forms as forms

from django_utils.form_helpers import DivForm,  FormValidator,  RecaptchaForm, disable_form

import django_community.utils
import django_utils.form_widgets as form_widgets
import django_utils.html_helpers as html_helpers
import django_utils.form_fields as form_fields
import django_qa.models as models
import django_qa.settings as settings

def build_flag_question_form():
    from django_moderation.config import DEFAULT_REASONS
    from django_moderation.forms import build_flag_form
    
    FLAG_QUESTION_ACTIONS = (('close', 'flag to close'), ('delete', 'flag for deletion'), ('cleanup', 'flag for cleanup'))
    REASONS = (DEFAULT_REASONS['offensive'],
               DEFAULT_REASONS['invalid'],
               DEFAULT_REASONS['advertising'],
               DEFAULT_REASONS['duplicate'],
               DEFAULT_REASONS['unrelated'],
               DEFAULT_REASONS['unclear'])
    return build_flag_form(FLAG_QUESTION_ACTIONS, REASONS)

def build_flag_answer_form():
    from django_moderation.config import DEFAULT_REASONS
    from django_moderation.forms import build_flag_form
    
    FLAG_ANSWER_ACTIONS = (('delete', 'flag for deletion'), ('cleanup', 'flag for cleanup'))
    REASONS = (DEFAULT_REASONS['offensive'],
               DEFAULT_REASONS['invalid'],
               DEFAULT_REASONS['advertising'],
               DEFAULT_REASONS['duplicate'],
               DEFAULT_REASONS['unrelated'],
               DEFAULT_REASONS['unclear'])
    return build_flag_form(FLAG_ANSWER_ACTIONS, REASONS)

def build_question_form(question = None, disabled = False):
    base_fields = {'title':  forms.CharField(max_length = 200,  min_length = 3,  required = True,  label = 'Title',  
                             widget = form_widgets.StandardCharfield(attrs={'class':'required question_form',  'minlength':'3'})) , 
                    'question': form_fields.WMDField(max_length = 5000,  
                                min_length = 5, 
                                widget = form_widgets.WMDTextarea(attrs={'class':'required',  'minlength':'10'}, preview_id='question_form_wmd_preview'), 
                                required = True, 
                                label = '', 
                                help_text = 'What is this question?. Be descriptive. Required.'),
                    'tags': forms.CharField(max_length = 200, 
                                min_length = 3, 
                                required = True, 
                                widget = form_widgets.StandardCharfield(attrs={'class':'required question_form',  'minlength':'3'}), 
                                help_text = 'Combine multiple words into single-words. Seperate tags using commas. Maximum five tags. At least one tag required.')
                    }
    
    if question:
        del base_fields['tags']
        base_fields['title'].initial = question.name
        base_fields['question'].initial = question.question
    
    def clean_title(self):
        title = self.data['title']
        if not models.Question.objects.can_add(self.user):
            raise forms.ValidationError("You can only ask a max of 5 questions per day.  Please wait to ask more.")
        if not question and models.Question.objects.filter(name__iexact = title):
            raise forms.ValidationError("There is already a question with that title.")
        if question:
            try:
                existing_question = models.Question.objects.get(name__iexact = title)
                if not existing_question.id == question.id:
                    raise forms.ValidationError("There is already a question with that title.")
            except ObjectDoesNotExist:
                pass
        return title
    
    QuestionForm = type('QuestionForm',  (DivForm, ),  base_fields)
    QuestionForm.clean_title = clean_title
    if disabled:
        disable_form(QuestionForm)
    return QuestionForm

def build_answer_form(answer = None, disabled = False):
    base_fields = {'answer': form_fields.WMDField(max_length = 2000,  
                                min_length = 5,  
                                widget = form_widgets.WMDTextarea(attrs={'class':'required',  'minlength':'10'}, preview_id='answer_form_wmd_preview'), 
                                required = True, 
                                label = '', 
                                help_text = 'Markdown enabled.')
                           }
    if answer:
        base_fields['answer'].initial = answer.answer
        base_fields['answer'].label = 'Answer'
    
    def clean_answer(self):
        answer = self.cleaned_data['answer']
        if not settings.MULTIPLE_ANSWERS_PER_USER and models.Answer.objects.filter(question = self.question, user = self.user):
            raise forms.ValidationError("You can ony submit one answer per question.  Please edit the answer you posted previously.")
        return answer
    
    AnswerForm = type('AnswerForm',  (DivForm, ),  base_fields)
    if disabled:
        disable_form(AnswerForm)
    return AnswerForm
