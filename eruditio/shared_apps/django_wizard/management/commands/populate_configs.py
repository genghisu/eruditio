import os

from django.core.management.base import NoArgsCommand, CommandError
from django.conf import settings

class Command(NoArgsCommand):
    help = "Initialize app defined configurations used by django_wizard."

    requires_model_validation = False
    can_import_settings = False
    
    def handle_noargs(self, **options):
        from django_wizard.autodiscover import autodiscover
        
        print "---Loading app configuration definitions---"
        autodiscover()
        print "---Creating configuration directory---"
        if not os.path.exists(os.path.join(settings.PROJECT_ROOT, 'django_wizard_configurations')):
            os.mkdir(os.path.join(settings.PROJECT_ROOT, 'django_wizard_configurations'))