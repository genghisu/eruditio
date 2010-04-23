import django_comments.models
import django_comments.config as config

def comments_config(request):
    """
    Allows django_comments configs to be used through the template context.
    """
    return {'COMMENT_HIDE_THRESHOLD' : getattr(config, 'COMMENT_HIDE_THRESHOLD')}