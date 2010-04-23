import django.forms as forms

import django_utils.form_widgets as form_widgets
import django_utils.html_helpers as html_helpers
import django_utils.form_helpers as form_helpers
from tagging.models import Tag

def build_retag_form(object):
    initial_tags = [tag.name for tag in Tag.objects.get_for_object(object)]
    tags_as_string = ",".join(initial_tags)
    base_fields = {'tags' : forms.CharField(max_length = 200,  
                            required = True,
                            initial = tags_as_string,
                            widget = form_widgets.StandardCharfield(attrs={'class':'required question_form'}), 
                            help_text = 'Combine multiple words into single-words. Seperate tags using commas. Maximum five tags. At least one tag required.')}
    
    RetagForm = type('RetagForm',  (form_helpers.DivForm, ),  base_fields)
    return RetagForm