import os
try:
    import json
except:
    import simplejson as json

from django.db import models, connection
from django.utils.translation import ugettext_lazy as _
from django.core.management.commands import loaddata
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from south.management.commands.syncdb import Command as SouthCommand
from south.db import db

base_dir = os.path.split(__file__)[0]
ct_fixture_name = os.path.join(base_dir, 'content_types.json')
                                       
class Command(SouthCommand):
    def handle_noargs(self, **options):
        print "---running modified syncdb---"
        verbosity = int(options.get('verbosity', 1))
        
        tables = connection.introspection.table_names()
        if not 'django_content_type' in tables:
            db.create_table('django_content_type', (
                ('id', models.AutoField(primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('app_label', models.CharField(max_length=100)),
                ('model', models.CharField(_('python model class name'), max_length=100)),
            ))
            db.create_unique('django_content_type', ('app_label', 'model'))

        loaddata.Command().execute(ct_fixture_name, verbosity = verbosity)
        options['migrate'], options['interactive'] = True, False
        super(Command, self).handle_noargs(**options)
        
        def ct_match_exist(content_types, id, name, app_label, model):
            for item in content_types:
                if item['model'] == 'contenttypes.contenttype' and \
                   item['pk'] == id and \
                   item['fields']['name'] == name and \
                   item['fields']['app_label'] == app_label and \
                   item['fields']['model'] == model:
                    return True
            return False
        content_types = json.load(open(ct_fixture_name))

        # check that no unexpected content types have been added
        for ct in ContentType.objects.all():
            if not ct_match_exist(content_types, ct.id, ct.name, ct.app_label, ct.model):
                ctdict =  { 'id': ct.id, 'name': ct.name, 'app_label':
                           ct.app_label, 'model': ct.model } 
                raise ValueError(""""An unexpected content type was found in the database.  You need to add it to the fixture file in 
                                 core/management/commands/content_types.json."
                                 {
                                    "pk": %(id)-s,
                                    "model": "contenttypes.contenttype",
                                    "fields": {
                                         "model": "%(model)-s",
                                         "name": "%(name)-s",
                                         "app_label": "%(app_label)-s"
                                    }
                                }
                                """ % (ctdict))