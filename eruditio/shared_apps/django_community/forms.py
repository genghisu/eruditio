import hashlib
import re
from recaptcha.client import captcha

from django.conf import settings
import django.forms as forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ValidationError
from django.contrib.auth.models import User

from django_utils.form_helpers import DivForm,  DynamicRequestForm, FormValidator
import django_utils.form_widgets as widgets
from django_utils import request_helpers
import django_community.models
import django_community.utils

class LoginForm(DivForm):
    """
    Form used to authenticate users to the site.
    """
    username = forms.CharField(max_length = 30,  
                               min_length = 2,  
                               required = True,  
                               label = 'Username',  
                               widget = widgets.StandardCharfield(attrs={'class':'required'}))
    password = forms.CharField(min_length = 3,  
                               label = 'Password',  
                               widget = widgets.StandardPassfield(attrs={'class':'required'}))
    
    def clean(self):
        result = super(LoginForm,  self).clean()
        try:
            name = self.cleaned_data['username']
            password = self.cleaned_data['password']
        except KeyError:
            raise forms.ValidationError("You have entered an invalid username and password combination.")
        
        try:
            user = User.objects.get(username = name)
        except ObjectDoesNotExist:
            user = None
            raise forms.ValidationError("You have entered an invalid username and password combination.")
        
        if not user or not user.check_password(password):
            raise forms.ValidationError("You have entered an invalid username and password combination.")
        return result
    
    def get_user(self):
        username = self.data['username']
        user = User.objects.get(username = username)
        return user
    
class SignupForm(DynamicRequestForm):
    """
    Form which allows users to sign up for the site.
    """
    username = forms.CharField(max_length = 30,  min_length = 2,  required = True,  label = 'Name:',  
                               widget = widgets.StandardCharfield(attrs={'class':'required',  'minlength':'3'}))
    email = forms.EmailField(label = 'Email:',  widget = widgets.StandardCharfield(attrs={'class':'required email'}))
    password = forms.CharField(min_length = 3,  label = 'Password:',  
                               widget = widgets.StandardPassfield(attrs={'class':'required'}))
    password_confirmation = forms.CharField(min_length = 3,  label = 'Password Confirmation:',  
                                            widget = widgets.StandardPassfield(attrs={'class':'required'}))
    captcha = forms.CharField(label = 'Are you human?', widget = widgets.RecaptchaField(),  required = False)
    
    def clean_username(self):
        name = self.cleaned_data['username']
        if not FormValidator.validate_username:
            raise forms.ValidationError("That username include invalid characters. Use letters, numbers and underscore.")
        else:
            try:
                User.objects.get(username = name)
                raise forms.ValidationError("That username has already been taken.")
            except ObjectDoesNotExist:
                pass
        return name
    
    def clean_password_confirmation(self):
        pw1 = self.cleaned_data['password']
        pw2 = self.cleaned_data['password_confirmation']
        if not pw1 == pw2:
            raise forms.ValidationError("Password confirmation does not match password.")
        return pw2
    
    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email = email)
            raise forms.ValidationError("There is already an user with this email address.")
        except ObjectDoesNotExist:
            pass
        return email
    
    def clean_captcha(self):
        value = None
        if self.request:
            challenge = self.data['recaptcha_challenge_field']
            response = self.data['recaptcha_response_field']
            captcha_response = captcha.submit(challenge,  response,  settings.RECAPTCHA_PRIVATE_KEY,  request_helpers.get_ip(self.request))
        if not captcha_response.is_valid:
            raise forms.ValidationError("Incorrect response entered.")
        return value

def build_edit_profile_form(user):
    """
    Returns an EditProfileForm which lets users edit their profiles.
    """
    profile = django_community.models.UserProfile.objects.get_user_profile(user)
    
    base_fields = {'display_name':  forms.CharField(max_length = 70,  min_length = 3,  required = False,  label = 'Display Name',  
                        initial = profile.display_name, 
                       widget = widgets.StandardCharfield(attrs={})) , 
                       'email': forms.EmailField(max_length = 200,  min_length = 5,  required = False,  label = 'Email', 
                        initial = user.email, 
                        widget = widgets.StandardCharfield(attrs={})), 
                        'first_name':  forms.CharField(max_length = 70,  required = False,  label = 'First Name',  
                            initial = user.first_name, 
                           widget = widgets.StandardCharfield(attrs={})) , 
                       'last_name':  forms.CharField(max_length = 70,  required = False,  label = 'Last Name',  
                            initial = user.last_name, 
                           widget = widgets.StandardCharfield(attrs={})) , 
                        'location':  forms.CharField(max_length = 70,  min_length = 3,  required = False,  label = 'Location',  
                            initial = profile.location, 
                           widget = widgets.StandardCharfield(attrs={})) , 
                        'website':  forms.URLField(max_length = 70,  min_length = 3,  required = False,  label = 'Website',  
                            initial = profile.website, 
                           widget = widgets.StandardCharfield(attrs={})) , 
                        'birthdate':  forms.DateTimeField(required = False,  
                                                          label = 'Birthday',  
                                                          initial = profile.birthdate, 
                                                          widget = widgets.StandardCharfield(attrs={}),
                                                          help_text = "YYYY-MM-DD.  Only used to calculate your age.") , 
                        'about_me':  forms.CharField(max_length = 500,  required = False,  label = 'About Me',  
                            initial = profile.about_me, 
                           widget = widgets.BigTextarea(attrs={})) , 
                       }
    
    def clean_display_name(self):
        display_name = self.cleaned_data['display_name']
        logged_user = self.request.user
        try:
            profile = django_community.models.UserProfile.objects.get(display_name = display_name)
            if not profile.user.pk == logged_user.pk:
                raise forms.ValidationError("That display name has already been taken.")
        except ObjectDoesNotExist:
            pass
        return display_name
         
    EditProfileForm = type('EditProfileForm',  (DynamicRequestForm, ),  base_fields)
    EditProfileForm.clean_display_name = clean_display_name
    return EditProfileForm
