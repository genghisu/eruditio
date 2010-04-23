try:
    import json
except:
    import simplejson as json
    
import django.forms as forms

import django_utils.form_widgets as form_widgets
import django_utils.html_helpers as html_helpers
import django_utils.form_helpers as form_helpers

def build_config_form(config, defined_config):
    available_options = json.loads(config.available_options)
    default = json.loads(defined_config.value)
    if available_options:
        CHOICES = [(x, x) for x in available_options]
        base_fields = {'value' : forms.ChoiceField(choices = CHOICES, 
                                                   required = True,
                                                   initial = default,
                                                   help_text = config.help_text)}
    else:
        base_fields = {'value': forms.CharField(max_length = 5000,  
                                                widget = form_widgets.GiantTextarea(attrs={'class':'required config_form'}), 
                                                required = False,
                                                initial = default,
                                                help_text = config.help_text)}
        
    ConfigForm = type('ConfigForm',  (form_helpers.DivForm, ),  base_fields)
    return ConfigForm

class SaveAsForm(form_helpers.DivForm):
    file = forms.CharField(max_length = 50,
                           widget = form_widgets.StandardCharfield(),
                           required = True,
                           initial = '',
                           help_text = 'Input a file name to save the current configuration to.')
    