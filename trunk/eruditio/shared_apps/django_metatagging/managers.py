from django.db import models, connection
import django.utils
from django.db import connection, models

from tagging.models import TaggedItem, Tag, TagManager
from tagging.utils import calculate_cloud, get_tag_list, get_queryset_and_model, parse_tag_input

qn = connection.ops.quote_name

class MetaTagManager(models.Manager):
    def most_active(self, content_type_id, num):
        """
        Returns a list of Tag objects for a particular @content_type_id
        sorted by the number of objects which have each Tag in descending order.  
        Returns a max of @num objects.
        """
        select_query = {'tag_count': \
                        """SELECT COUNT(*) FROM %(tagged_item)s
                        WHERE %(tag)s.id = %(tagged_item)s.tag_id
                        AND %(tagged_item)s.content_type_id = %(content_type_id)s
                        """ % {
                            'tagged_item' : connection.ops.quote_name(TaggedItem._meta.db_table),
                            'tag' : connection.ops.quote_name(self.model._meta.db_table),
                            'content_type_id' : content_type_id
                            }
                        }
        active_tags = self.model.objects.all().extra(select = select_query).order_by('-tag_count')[0:num]
        return active_tags
    
    def count_tags(self, tags, model = None):
        """
        Attaches a count attribute to a QuerySet of @tags.
        """
        for tag in tags:
            if not model:
                tag.count = TaggedItem.objects.filter(tag = tag).count()
            else:
                content_type_object = ContentType.objects.get_for_model(model)
                tag.count = TaggedItem.objects.filter(tag = tag, content_type = content_type_object)
        return tags
    
    def retag(self, object, tags):
        """
        Modifies the tags associated with @object so that @object 
        is tagged by all tags within the list @tags.
        """
        current_tags = [(x.name, x.id) for x in self.model.objects.get_for_object(object)]
        current_tag_names = [x.name for x in self.model.objects.get_for_object(object)]
        for tag in current_tags:
            if not tag[0] in tags:
                tag_model = self.model.objects.get(id = tag[1])
                tag_model.delete()
        for tag in tags:
            if not tag in current_tag_names:
                self.model.objects.add_tag(object, tag)
        final_tag_names = [x.name for x in self.model.objects.get_for_object(object)]
        return current_tag_names, final_tag_names

    def related_for_tags(self, tags, counts=False, min_count=None):
        """
        Obtain a list of tags related to a given list of tags - that
        is, other tags used by items which have all the given tags.

        If ``counts`` is True, a ``count`` attribute will be added to
        each tag, indicating the number of items which have it in
        addition to the given list of tags.

        If ``min_count`` is given, only tags which have a ``count``
        greater than or equal to ``min_count`` will be returned.
        Passing a value for ``min_count`` implies ``counts=True``.
        """
        if min_count is not None: counts = True
        tags = get_tag_list(tags)
        tag_count = len(tags)
        tagged_item_table = qn(TaggedItem._meta.db_table)
        query = """
        SELECT %(tag)s.id, %(tag)s.name%(count_sql)s
        FROM %(tagged_item)s INNER JOIN %(tag)s ON %(tagged_item)s.tag_id = %(tag)s.id
        WHERE %(tag)s.id NOT IN (%(tag_id_placeholders)s)
        GROUP BY %(tag)s.id, %(tag)s.name
        %(min_count_sql)s
        ORDER BY %(tag)s.name ASC""" % {
            'tag': qn(self.model._meta.db_table),
            'count_sql': counts and ', COUNT(%s.object_id)' % tagged_item_table or '',
            'tagged_item': tagged_item_table,
            'tag_id_placeholders': ','.join(['%s'] * tag_count),
            'tag_count': tag_count,
            'min_count_sql': min_count is not None and ('HAVING COUNT(%s.object_id) >= %%s' % tagged_item_table) or '',
        }
                
        params = [tag.pk for tag in tags]
        if min_count is not None:
            params.append(min_count)

        cursor = connection.cursor()
        cursor.execute(query, params)
        related = []
        for row in cursor.fetchall():
            tag = self.model(*row[:2])
            if counts is True:
                tag.count = row[2]
            related.append(tag)
        return related
    
Tag.meta_objects = MetaTagManager()
Tag.meta_objects.model = Tag