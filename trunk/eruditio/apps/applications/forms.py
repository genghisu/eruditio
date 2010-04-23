import django.forms as forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from django_utils.form_helpers import DivForm,  FormValidator,  RecaptchaForm, disable_form
from django_relatedcontent.forms import RelatedContentField, RelatedContentWidget
import django_community.utils
import django_utils.form_widgets as form_widgets
import django_utils.html_helpers as html_helpers
import django_utils.form_fields as form_fields

import applications.models as models
from core.models import Django, Python

def build_app_form(app = None, disabled = False):
    dependencies_content_type_object = ContentType.objects.get_for_model(models.App)
    dependencies_object_id = -1 # default id to denote new object
    dependencies_usage = 'dependency'
    
    base_fields = {'name' : forms.CharField(max_length = 75,  
                                            min_length = 3,  
                                            required = True,  
                                            label = 'App Name',  
                                            widget = form_widgets.BigCharfield(attrs={'class':'required'}),
                                            help_text = 'Must be <= 75 characters.'),
                                            
                    'version' : forms.CharField(max_length = 75,  
                                                min_length = 3,  
                                                required = True,  
                                                label = 'Version',  
                                                widget = form_widgets.BigCharfield(attrs={'class':'required'}),
                                                help_text = 'Version number.  Must be unique when combined with app name.'),
                                                
                    'url' : forms.URLField(max_length = 50,  
                                            min_length = 3,  
                                            required = True,  
                                            label = 'Homepage',  
                                            widget = form_widgets.BigCharfield(attrs={'class':'required'}),
                                            help_text = 'Required.  Homepage of this app.'),
                                            
                    'sources' : forms.CharField(max_length = 100,  
                                                min_length = 3,  
                                                required = True,  
                                                label = 'Sources',  
                                                widget = form_widgets.BigCharfield(),
                                                help_text = 'Location(s) where the source code can be downloaded from.  Comma separated.'),
                    
                    'description' : form_fields.WMDField(max_length = 2000,  
                                                        min_length = 15, 
                                                        widget = form_widgets.WMDTextarea(attrs={'class':'required',  'minlength':'10'}, preview_id='app_form_wmd_preview'), 
                                                        required = True, 
                                                        label = 'Description', 
                                                        help_text = 'Give a detailed description of this app.  Markdown enabled.'),
                    
                    'python' : forms.MultipleChoiceField(choices = Python.objects.versions(),
                                                         widget = forms.widgets.CheckboxSelectMultiple(),
                                                         label = 'Python Dependency',
                                                         help_text = 'Which versions of Python is this app compatible with?  Minimum one required.'),
                    
                    'django' : forms.MultipleChoiceField(widget = forms.widgets.CheckboxSelectMultiple(),
                                                         label = 'Django Dependency',
                                                         choices = Django.objects.versions(),
                                                         help_text = 'Which versions of Django is this app compatible with?  Minimum one required.'),
                    
                    'dependencies' : RelatedContentField(base_content_type = dependencies_content_type_object.id,
                                                         object_id = dependencies_object_id,
                                                         usage = dependencies_usage,
                                                         iframe_width = 800,
                                                         required = False,
                                                         iframe_height = 600,
                                                         help_text = 'Other apps on which this apps depends to function.'),
                    
                    'tags' : forms.CharField(max_length = 200, 
                                             required = True, 
                                             widget = form_widgets.StandardCharfield(attrs={'class':'required code_form'}), 
                                             help_text = 'Combine multiple words into single-words. Seperate tags using commas. Maximum five tags. At least one tag required.')
                }
    
    if app:
        del base_fields['dependencies']
        del base_fields['tags']
        base_fields['name'].initial = app.name
        base_fields['version'].initial = app.version
        base_fields['url'].initial = app.url
        base_fields['sources'].initial = ",".join(models.App.objects.sources(app))
        base_fields['description'].initial = app.description
        base_fields['python'].initial = models.App.objects.python_versions(app)
        base_fields['django'].initial = models.App.objects.django_versions(app)
    
    def clean_name(self):
        name = self.data['name']
        if not models.App.objects.can_add(self.user):
            raise forms.ValidationError("You can only submit a max of 5 django apps a day.  Please wait to submit more.")
        if models.App.objects.filter(name__iexact = name):
            raise forms.ValidationError("There is already an app with that name.")
        return name
    
    AppForm = type('AppForm', (DivForm, ), base_fields)
    AppForm.clean_name = clean_name
    if disabled:
        disable_form(AppForm)
    return AppForm

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

def build_edit_dependencies_form(app):
    dependencies_content_type_object = ContentType.objects.get_for_model(models.App)
    dependencies_object_id = app.id
    dependencies_usage = 'dependency'
    
    base_fields = {'dependencies' : RelatedContentField(base_content_type = dependencies_content_type_object.id,
                                                         object_id = dependencies_object_id,
                                                         usage = dependencies_usage,
                                                         iframe_width = 800,
                                                         required = False,
                                                         iframe_height = 600,
                                                         help_text = 'Other apps on which this apps depends to function.')}
    
    EditDependenciesForm = type('EditDependenciesForm',  (DivForm, ),  base_fields)
    return EditDependenciesForm