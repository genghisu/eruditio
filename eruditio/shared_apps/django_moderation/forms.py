import django.forms as forms

from django_utils.form_helpers import DivForm,  FormValidator,  RecaptchaForm
import django_utils.form_widgets as form_widgets

def build_flag_form(actions, reasons):
    """
    Generates a DivForm to be used for submitting content flags.
    """
    base_fields = {'action' : forms.ChoiceField(choices = actions, required = True),
                   'reason' : forms.ChoiceField(choices = reasons,  required = True),
                   'details' : forms.CharField(max_length = 500,  
                                               min_length = 1, 
                                               required = False, 
                                               widget = form_widgets.StandardTextarea(attrs={'class':'full_width'}), 
                                               label = 'Additional info.')
                   }
    
    FlagContentForm = type('FlagForm',  (DivForm, ),  base_fields)
    return FlagContentForm