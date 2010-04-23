import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django.contrib.auth.models import User
from core.models import Django, Python, Source, DjangoCompatibility, PythonCompatibility
from django_common.managers import LimitingManager, BaseObjectsManager
from django_relatedcontent.models import ContentAssociation
from django_moderation.managers import ModeratedContentManager, HiddenContentManager
import django_contenthistory.signals as signals

class AppManager(BaseObjectsManager, LimitingManager, HiddenContentManager):
    def add(self, user, data):
        if self.can_add(user):
            name = data.get('name', None)
            description = data.get('description', None)
            version = data.get('version', None),
            sources = data.get('sources', None)
            url = data.get('url', None)
            dependencies = data.get('dependencies', [])
            python_versions = data.get('python', [])
            django_versions = data.get('django', [])
            usage = 'dependency'
             
            name = name.replace(" ", "-")
            app = self.model(name = name, url = url, description = description, version = version, user = user)
            app.save()
            django_version_objects = self.edit_django_versions(app, django_versions)
            python_version_objects = self.edit_python_versions(app, python_versions)
            final_sources = self.edit_sources(app, sources)
            final_dependencies = self.edit_dependencies(app, dependencies, usage)
            
            signals.edit.send(sender=self.model, original=None, current=app, editor=user)
        else:
            app = None
        return app
    
    def django_versions(self, app):
        return Django.objects.versions_for_object(app)

    def python_versions(self, app):
        return Python.objects.versions_for_object(app)
        
    def edit_python_versions(self, app, versions):
        content_type_object = ContentType.objects.get_for_model(self.model)
        current_versions = PythonCompatibility.objects.filter(content_type = content_type_object, object_id = app.id)
        for version_object in current_versions:
            version_object.delete()
            
        python_version_objects = []
        version_numbers = [x.split('_')[1] for x in versions]
        for version in version_numbers:
            python_version_object = Python.objects.add_object_compatibility(app, version)
            python_version_objects.append(python_version_object)
        return python_version_objects

    def edit_django_versions(self, app, versions):
        content_type_object = ContentType.objects.get_for_model(self.model)
        current_versions = DjangoCompatibility.objects.filter(content_type = content_type_object, object_id = app.id)
        for version_object in current_versions:
            version_object.delete()
            
        django_version_objects = []
        version_numbers = [x.split('_')[1] for x in versions]
        for version in version_numbers:
            django_version_object = Django.objects.add_object_compatibility(app, version)
            django_version_objects.append(django_version_object)
        return django_version_objects
    
    def edit_sources(self, app, sources):
        content_type_object = ContentType.objects.get_for_model(self.model)
        current_sources = Source.objects.filter(content_type = content_type_object, object_id = app.id)
        parsed_sources = Source.objects.parse_source_data(sources)
        for source_object in current_sources:
            source_object.delete()
            
        final_sources = Source.objects.add_sources(app, parsed_sources)
        return final_sources
    
    def edit_dependencies(self, app, dependencies, usage):
        dependencies = ContentAssociation.objects.add_associations(app, usage, dependencies)
        return dependencies
    
    def count_dependencies(self):
        count = ContentAssociation.objects.associations_for_object(self, 'dependency', self.model).count()
        return count
    
    def sources(self, app):
        content_type_object = ContentType.objects.get_for_model(self.model)
        return [source.uri for source in Source.objects.filter(content_type = content_type_object,
                                                                object_id = app.id)]
        
    def edit(self, app, user, data):
        name = data.get('name', None)
        description = data.get('description', None)
        version = data.get('version', None),
        sources = data.get('sources', None)
        url = data.get('url', None)
        python_versions = data.get('python', [])
        django_versions = data.get('django', [])
        
        original = self.model.objects.get(id = app.id)
        app.name = name
        app.description = description
        app.version = version
        app.url = url
        app.save()
        django_version_objects = self.edit_django_versions(app, django_versions)
        python_version_objects = self.edit_python_versions(app, python_versions)
        final_sources = self.edit_sources(app, sources)
        
        signals.edit.send(sender=self.model, original=original, current=app, editor=user)
        return app
    
class App(models.Model):
    name = models.CharField(max_length = 75)
    description = models.TextField()
    version = models.CharField(max_length = 75)
    url = models.URLField()
    user = models.ForeignKey(User)
    
    date_created = CreationDateTimeField()
    date_modified = ModificationDateTimeField()
    
    objects = AppManager()
    
    def count_dependencies(self):
        return ContentAssociation.objects.associations_for_object(self, 'dependency', App).count()
    
    def __unicode__(self):
        return self.name
    
class AppPackage(models.Model):
    name = models.CharField(max_length = 75)
    description = models.TextField()
    user = models.ForeignKey(User)
    
    date_created = CreationDateTimeField()
    date_modified = ModificationDateTimeField()
    
class AppPackageItem(models.Model):
    app = models.ForeignKey(App)
    package = models.ForeignKey(AppPackage)