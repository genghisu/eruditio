import django.forms as forms

from django_utils.form_helpers import DivForm,  FormValidator
import django_utils.form_widgets as form_widgets
import django_comments.models as models

def build_comment_form(comment_class):
    """
    Returns a CommentForm based on the comment_class given.
    
    The parameter comment_class allows for multiple versions of CommentForm
    to be created depending on which part of the site the comments
    appear in.
    """
    if comment_class == 'compact':
        base_fields = {'comment':  forms.CharField(max_length = 500,  
                                    min_length = 10, 
                                    widget = form_widgets.SmallTextarea(attrs={'class':'required',  'minlength':'10'}), 
                                    required = True, 
                                    help_text = 'Only text allowed.  HTML tags will be stripped.',
                                    label = '')
                                   }
    elif comment_class == 'standard':
        base_fields = {'comment':  forms.CharField(max_length = 500,  
                                    min_length = 10, 
                                    widget = form_widgets.BigTextarea(attrs={'class':'required',  'minlength':'10'}), 
                                    required = True,
                                    help_text = 'Only text allowed.  HTML tags will be stripped.',
                                    label = '')
                              }
    
    CommentForm = type('CommentForm', (DivForm, ), base_fields)
    return CommentForm

def build_edit_comment_form(comment):
    """
    Returns an EditCommentForm which allows for the editing of comments.
    
    Does not depend on comment_class due to it being displayed at its own unique view.
    """
    base_fields = {'comment':  forms.CharField(max_length = 500,  
                            min_length = 10, 
                            widget = form_widgets.BigTextarea(attrs={'class':'required',  'minlength':'10'}), 
                            required = True, 
                            initial = comment.content, 
                            label = '')
                           }
    
    EditCommentForm = type('EditCommentForm',  (DivForm, ),  base_fields)
    return EditCommentForm
