from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField

class DjangoManager(models.Manager):
    def versions(self):
        return [("django_%s" % (x.version), "Django %s" % (x.version)) for x in self.model.objects.all().order_by("version")]
    
    def add_object_compatibility(self, object, version):
        try:
            django_object = self.model.objects.get(version = version)
        except ObjectDoesNotExist:
            django_object = None
        
        content_type_object = ContentType.objects.get_for_model(object.__class__)
        try:
            comp = DjangoCompatibility.objects.get(content_type = content_type_object, 
                                                   object_id = object.id, 
                                                   django = django_object)
        except ObjectDoesNotExist:
            comp = DjangoCompatibility(content_type = content_type_object, object_id = object.id, django = django_object)
            comp.save()
        return comp
    
    def versions_for_object(self, object):
        content_type_object = ContentType.objects.get_for_model(object.__class__)
        return ["django_%s" % (x.django.version) for x in DjangoCompatibility.objects.filter(content_type = content_type_object, object_id = object.id)]
    
class PythonManager(models.Manager):
    def versions(self):
        return [("python_%s" % (x.version), "Python %s" % (x.version)) for x in self.model.objects.all().order_by("version")]
    
    def add_object_compatibility(self, object, version):
        try:
            python_object = self.model.objects.get(version = version)
        except ObjectDoesNotExist:
            python_object = None
        
        content_type_object = ContentType.objects.get_for_model(object.__class__)
        try:
            comp = PythonCompatibility.objects.get(content_type = content_type_object, 
                                                   object_id = object.id, 
                                                   python = python_object)
        except ObjectDoesNotExist:
            comp = PythonCompatibility(content_type = content_type_object, object_id = object.id, python = python_object)
            comp.save()
        return comp
    
    def versions_for_object(self, object):
        content_type_object = ContentType.objects.get_for_model(object.__class__)
        return ["python_%s" % (x.python.version) for x in PythonCompatibility.objects.filter(content_type = content_type_object, object_id = object.id)]
    
class SourceManager(models.Manager):
    def parse_source_data(self, data):
        import re
        final_sources = []
        sources = [x for x in data.split(",") if x.strip()]
        for source in sources:
            uri = source
            final_sources.append(('http', uri))
        return final_sources
    
    def add_sources(self, object, sources):
        final_sources = []
        for source in sources:
            source_object = self.model.objects.add_source(object, source[0], source[1])
            final_sources.append(source_object)
        return final_sources
                                                           
    def add_source(self, object, protocol, uri):
        content_type_object = ContentType.objects.get_for_model(object.__class__)
        object_id = object.id
        mode = SourceMode.objects.get(name = protocol)
        source = self.model(active = True,
                            content_type = content_type_object,
                            object_id = object_id,
                            mode = mode,
                            uri = uri)
        source.save()
        return source
    
class SourceMode(models.Model):
    name = models.CharField(max_length = 75, unique = True)
    
    def __unicode__(self):
        return self.name
    
class Source(models.Model):
    active = models.BooleanField(default = True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    mode = models.ForeignKey(SourceMode)
    uri = models.TextField()
    
    date_created = CreationDateTimeField()
    date_modified = ModificationDateTimeField()
    
    objects = SourceManager()
    
    def __unicode__(self):
        return "%s::%s" % (self.mode.name, self.uri)
    
class PythonPackage(models.Model):
    name = models.CharField(max_length = 75)
    version = models.TextField()

class PythonPackageDependency(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    base_object = generic.GenericForeignKey()
    
    depends_on = models.ForeignKey(PythonPackage)

class Django(models.Model):
    version = models.CharField(max_length = 75, unique = True)
    
    objects = DjangoManager()
    
    def __unicode__(self):
        return "Django %s" % (self.version)
    
class Python(models.Model):
    version = models.CharField(max_length = 75, unique = True)
    
    objects = PythonManager()
    
    def __unicode__(self):
        return "Python %s" % (self.version)

class DjangoCompatibility(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    base_object = generic.GenericForeignKey()
    
    django = models.ForeignKey(Django)
    
    def name(self):
        return self.django.__unicode__()

class PythonCompatibility(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    base_object = generic.GenericForeignKey()
    
    python = models.ForeignKey(Python)
    
    def name(self):
        return self.python.__unicode__()