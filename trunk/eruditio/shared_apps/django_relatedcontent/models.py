from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django_relatedcontent.utils import parse_relatedcontent_data

class ContentUsageManager(models.Manager):
    def usage_for_base_content_type(self, base_content_type, usage):
        """
        Return all AvailableContentUsage objects that have base_model = base_content_type.
        """
        base_content_type_object = ContentType.objects.get(id = base_content_type)
        
        if usage == 'all':
            available_usages = AvailableContentUsage.objects.filter(base_model = base_content_type_object)
        else:
            content_usage = self.model.objects.get_usage_object(usage)
            available_usages = AvailableContentUsage.objects.filter(base_model = base_content_type_object,
                                                                    usage = content_usage)
        return available_usages
    
    def get_usage_object(self, usage):
        """
        Helper method for getting a ContentUsage agnostic to str and ContentUsage classes.
        """
        if usage.__class__ == ContentUsage:
            content_usage_object = usage
        else:
            try:
                content_usage_object = self.model.objects.get(name = str(usage))
            except Exception, e:
                content_usage_object = None
                raise ObjectDoesNotExist("ContentUsage %s does not exist" % (str(usage)))
        return content_usage_object
    
class ContentAssociationManager(models.Manager):
    def add_association(self, base_content_type, base_object_id, selectable_content_type, selectable_object_id, usage, order = None):
        """
        Creates a ContentAssociation instance between two objects.
        """
        try:
            association_object = self.model.objects.get(parent_content_type = base_content_type,
                                        parent_object_id = base_object_id,
                                        child_content_type = selectable_content_type,
                                        child_object_id = selectable_object_id,
                                        usage = usage)
        except ObjectDoesNotExist:
            if not order:
                order = self.model.objects.get_max_usage_count(base_content_type, base_object_id, usage) + 1
            association_object = self.model(parent_content_type = base_content_type,
                                        parent_object_id = base_object_id,
                                        child_content_type = selectable_content_type,
                                        child_object_id = selectable_object_id,
                                        usage = usage,
                                        order = order)
            association_object.save()
        return association_object
    
    def remove_association(self, base_content_type, base_object_id, selectable_content_type, selectable_object_id, usage):
        """
        Removes an existing ContentAssociation between two objects.
        """
        try:
            association_object = self.model.objects.get(parent_content_type = base_content_type,
                                        parent_object_id = base_object_id,
                                        child_content_type = selectable_content_type,
                                        child_object_id = selectable_object_id,
                                        usage = usage)
            association_object.delete()
        except ObjectDoesNotExist:
            pass
    
    def add_associations(self, object, usage, association_data):
        """
        Add multiple ContentAssociations based on association_data.
        """
        usage_object = ContentUsage.objects.get_usage_object(usage)

            
        base_content_type = ContentType.objects.get_for_model(object.__class__)
        base_object_id = object.id
        
        parsed_associations = parse_relatedcontent_data(association_data)
        final_associations = []
        current_order = self.model.objects.get_max_usage_count(base_content_type, base_object_id, usage_object)
        for association in parsed_associations:
            current_order = current_order + 1
            selectable_content_type = ContentType.objects.get(id = int(association[0]))
            selectable_object_id = int(association[1])
            association_object = self.model.objects.add_association(base_content_type,
                                                                   base_object_id,
                                                                   selectable_content_type,
                                                                   selectable_object_id,
                                                                   usage_object,
                                                                   current_order)
            final_associations.append(association_object)
        return final_associations
    
    def get_max_usage_count(self, base_content_type, base_object_id, usage):
        """
        Return the current number of ContentAssociation objects associated
        with base_object and usage.
        """
        return self.model.objects.filter(parent_content_type = base_content_type,
                                         parent_object_id = base_object_id,
                                         usage = usage).count()
    
    def associations_for_object(self, object, usage, model = None):
        """
        Returns all ContentAssociations for an object of mode usage.
        model can be set to filter on child content_type.
        """
        usage_object = ContentUsage.objects.get_usage_object(usage)
            
        base_content_type = ContentType.objects.get_for_model(object.__class__)
        base_object_id = object.id
        
        if model:
            child_content_type = ContentType.objects.get_for_model(model)
            associations = self.model.objects.filter(parent_content_type = base_content_type,
                                                 parent_object_id = base_object_id,
                                                 child_content_type = child_content_type,
                                                 usage = usage_object).order_by('order')
        else:
            associations = self.model.objects.filter(parent_content_type = base_content_type,
                                                 parent_object_id = base_object_id,
                                                 usage = usage_object).order_by('order')
        return associations

class ContentUsage(models.Model):
    """
    Top level mode of association.
    """
    name = models.CharField(max_length = 75, unique = True)
    
    objects = ContentUsageManager()
    
    def __unicode__(self):
        return self.name
    
class All(models.Model):
    """
    Place holder content type representing all available contenttypes.
    Used for denoting content usage associations that are available
    to all content types.
    """
    pass

class AvailableContentUsage(models.Model):
    """
    Represents an association mode between two content types.
    base_model represents the primary content type of the M2M relationship.
    selectable_model represents the content type that is to be associated with
    the base_model.
    """
    usage = models.ForeignKey(ContentUsage)
    base_model = models.ForeignKey(ContentType, related_name = 'base_model')
    selectable_model = models.ForeignKey(ContentType, related_name = 'selectable_model')
    
    def __unicode__(self):
        return "%s between %s and %s" % (self.usage.name, self.base_model.name, self.selectable_model.name)
    
class ContentAssociation(models.Model):
    """
    M2M table representing the associations between objects.
    parent is the primary object.
    child is the associated object.
    """
    usage = models.ForeignKey(ContentUsage)
    order = models.IntegerField()
    
    parent_content_type = models.ForeignKey(ContentType,  related_name = 'parent_content_type')
    parent_object_id = models.PositiveIntegerField()
    parent = generic.GenericForeignKey('parent_content_type',  'parent_object_id')
    
    child_content_type = models.ForeignKey(ContentType,  related_name = 'child_content_type')
    child_object_id = models.PositiveIntegerField()
    child = generic.GenericForeignKey('child_content_type',  'child_object_id')
    
    date_created = CreationDateTimeField()
    date_modified = ModificationDateTimeField()
    
    objects = ContentAssociationManager()