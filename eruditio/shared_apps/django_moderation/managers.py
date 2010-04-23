from django.db import models

from django.contrib.contenttypes.models import ContentType
from django_moderation.models import ContentFlagInstance, ContentFlag
from django.db.models.query import QuerySet
import django_moderation.config as settings

class ModeratedContentManager(models.Manager):
    """
    Manager class which moderated content types should subclass their Managers
    from.
    """
    def get_query_set(self):
        base_query_set = base_query_set = QuerySet(self.model)
        model_content_type_object = ContentType.objects.get_for_model(self.model)
        values = {}
        values['model_content_type'] = model_content_type_object.id
        values['model_table'] = self.model._meta.db_table
        values['flag_table'] = ContentFlagInstance._meta.db_table
        values['moderate_flag'] = ContentFlag.objects.get(name = ContentFlag.ACCEPT_FLAG).id
        
        where_clause = """((SELECT COUNT(*) FROM %(flag_table)s WHERE
                            %(flag_table)s.content_type_id = %(model_content_type)s AND
                            %(flag_table)s.object_id = %(model_table)s.id AND
                            %(flag_table)s.flag_id = %(moderate_flag)s) > 0)""" % values
        
        return base_query_set.extra(where = [where_clause])
    
    def get_all(self, *args, **kwargs):
        return QuerySet(self.model).get(*args, **kwargs)
    
class HiddenContentManager(models.Manager):
    """
    Manager class which all models which want to hide 
    """
    def get_query_set(self):
        model_content_type_object = ContentType.objects.get_for_model(self.model)
        values = {}
        values['model_content_type'] = model_content_type_object.id
        values['model_table'] = self.model._meta.db_table
        values['flag_table'] = ContentFlagInstance._meta.db_table
        values['hide_flag'] = ContentFlag.objects.get(name = ContentFlag.HIDDEN_FLAG).id
        
        base_query_set = QuerySet(self.model)
        where_clause = """((SELECT COUNT(*) FROM %(flag_table)s WHERE
                            %(flag_table)s.content_type_id = %(model_content_type)s AND
                            %(flag_table)s.object_id = %(model_table)s.id AND
                            %(flag_table)s.flag_id = %(hide_flag)s) = 0)""" % values
        return base_query_set.extra(where = [where_clause])