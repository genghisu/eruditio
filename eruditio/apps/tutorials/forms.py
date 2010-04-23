import django.forms as forms

from django_utils.form_helpers import DivForm,  FormValidator,  RecaptchaForm, disable_form

import django_community.utils
import django_utils.form_widgets as form_widgets
import django_utils.html_helpers as html_helpers
import tutorials.models as models
import django_utils.form_fields as form_fields

def build_tutorial_form(tutorial = None, disabled = False):
    base_fields = {'name' : forms.CharField(max_length = 75,  
                                            min_length = 3,  
                                            required = True,  
                                            label = 'Tutorial Name', 
                                            widget = form_widgets.BigCharfield(attrs={'class':'required',  'minlength':'3'}),
                                            help_text = 'Must be <= 75 characters.'),
                                            
                    'description' : form_fields.WMDField(max_length = 2000,  
                                                        min_length = 15, 
                                                        widget = form_widgets.WMDTextarea(attrs={'class':'required',  'minlength':'3', 'rows':15}, preview_id='tutorial_form_wmd_preview'), 
                                                        required = True, 
                                                        label = 'Description', 
                                                        help_text = 'Description of this tutorial.  Markdown enabled.'),
                                
                    'url' : forms.CharField(max_length = 70,  
                                            min_length = 6,  
                                            required = True,  
                                            label = 'URL', 
                                            widget = form_widgets.BigCharfield(attrs={'class':'required',  'minlength':'6'}),
                                            help_text = 'Location of this tutorial.'),
                    
                    'tags': forms.CharField(max_length = 200, 
                                required = True, 
                                widget = form_widgets.StandardCharfield(attrs={'class':'required code_form'}), 
                                help_text = 'Combine multiple words into single-words. Seperate tags using commas. Maximum five tags. At least one tag required.')
                }
    
    if tutorial:
        del base_fields['tags']
        base_fields['name'].initial = tutorial.name
        base_fields['description'].initial = tutorial.description
        base_fields['url'].initial = tutorial.url
    
    def clean_name(self):
        name = self.data['name']
        if not models.Tutorial.objects.can_add(self.user):
            raise forms.ValidationError("You can only submit a max of 5 django tutorials a day.  Please wait to submit more.")
        if models.Tutorial.objects.filter(name__iexact = name):
            raise forms.ValidationError("There is already a tutorial with that name.")
        return name
    
    TutorialForm = type('TutorialForm',  (DivForm, ),  base_fields)
    TutorialForm.clean_name = clean_name
    if disabled:
        disable_form(TutorialForm)
    return TutorialForm

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