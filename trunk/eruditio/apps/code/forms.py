import django.forms as forms

from django_utils.form_helpers import DivForm,  FormValidator,  RecaptchaForm, disable_form

import django_community.utils
import django_utils.form_widgets as form_widgets
import django_utils.html_helpers as html_helpers
import django_utils.form_fields as form_fields
import code.models as models

def build_code_form(code = None, disabled = False):
    base_fields = {'title': forms.CharField(max_length = 70,  
                                            min_length = 3,  
                                            required = True,  
                                            label = 'Code Name',  
                                            widget = form_widgets.BigCharfield(attrs={'class':'required code_form',  'minlength':'3'}),
                                            help_text = 'Must be <= 75 characters.'),
                                            
                    'mode': forms.ChoiceField(choices = models.CodeMode.MODES, 
                                              help_text = 'What kind of code snippet is this?'),
                                              
                    'description': form_fields.WMDField(max_length = 2000,  
                                                        min_length = 15, 
                                                        widget = form_widgets.WMDTextarea(attrs={'class':'required',  'minlength':'3'}, preview_id='code_form_wmd_preview'), 
                                                        required = True, 
                                                        help_text = 'Give a detailed description of this code snippet.  Markdown enabled.'),
                    
                    'code': forms.CharField(max_length = 5000,  
                                            min_length = 25, 
                                            widget = form_widgets.GiantTextarea(attrs={'class':'required code_form',  'minlength':'5'}), 
                                            required = True, 
                                            label = 'Code', 
                                            help_text = 'The actual code.'),
                                            
                    'tags': forms.CharField(max_length = 200, 
                                required = True, 
                                widget = form_widgets.StandardCharfield(attrs={'class':'required code_form'}), 
                                help_text = 'Combine multiple words into single-words. Seperate tags using commas. Maximum five tags. At least one tag required.')
                    }
    
    if code:
        del base_fields['tags']
        base_fields['title'].initial = code.name
        base_fields['mode'].initial = code.mode.name
        base_fields['description'].initial = code.description
        base_fields['code'].initial = code.code
        
    def clean_title(self):
        title = self.data['title']
        mode = self.data['mode']
        
        try:
            code_mode = models.CodeMode.objects.get(name = mode)
        except ObjectDoesNotExist:
            code_mode = None
                
        if models.Code.objects.filter(name__iexact = title, mode = code_mode):
            raise forms.ValidationError("A code snippet with that title already exists.")
        if not models.Code.objects.can_add(self.user):
            raise forms.ValidationError("You can only submit a max of 5 code snippets a day.  Please wait to submit more.")
        return title
    
    def clean_code(self):
        code = self.cleaned_data['code']
        return code
    
    CodeForm = type('CodeForm',  (DivForm, ),  base_fields)
    CodeForm.clean_title = clean_title
    if disabled:
        disable_form(CodeForm)
    return CodeForm

def build_flag_form():
    from django_moderation.config import DEFAULT_REASONS
    from django_moderation.forms import build_flag_form
    
    FLAG_ACTIONS = (('close', 'flag to close'), ('delete', 'flag for deletion'), ('cleanup', 'flag for cleanup'))
    REASONS = (DEFAULT_REASONS['offensive'],
               DEFAULT_REASONS['invalid'],
               DEFAULT_REASONS['advertising'],
               DEFAULT_REASONS['duplicate'],
               DEFAULT_REASONS['unrelated'],
               DEFAULT_REASONS['unclear'])
    return build_flag_form(FLAG_ACTIONS, REASONS)