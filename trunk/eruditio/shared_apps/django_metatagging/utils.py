from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from tagging.models import Tag, TaggedItem
from tagging.utils import get_tag, get_queryset_and_model, parse_tag_input

def tagged_objects(content_type = None, tag = None, related_tags = False, related_tag_counts = True, **kwargs):
    """
    Returns a queryset of objects of a target content type with the given tag and a list of related tags 
    if related_tags = True.
    """
    if content_type is None:
        raise AttributeError(_('tagged_objects must be called with a content type'))
    else:
        try:
            model_content_type = ContentType.objects.get(id = int(content_type))
        except ObjectDoesNotExist:
            raise AttributeError(_('tagged_objects must be called with a valid content type'))

    if tag is None:
        raise AttributeError(_('tagged_objects must be called with a tag.'))
    
    tag_instance = get_tag(tag)
    if tag_instance is None:
        raise AttributeError(_('tagged_object must be called with a valid tag'))
    
    queryset = TaggedItem.objects.get_by_model(model_content_type.model_class(), tag_instance)
    if related_tags:
        related_tags_list = \
            Tag.objects.related_for_model(tag_instance, queryset, counts = related_tag_counts)
    else:
        related_tags_list = []
        
    return queryset, related_tags_list

def all_tagged_objects(tag = None, related_tags = False, related_tag_counts = True, **kwargs):
    """
    Returns a queryset of all objects that have been tagged with tag and a list of related
    tags if related_tags = True.
    """
    if tag is None:
        raise AttributeError(_('tagged_objects must be called with a tag.'))
    
    tag_instance = get_tag(tag)
    if tag_instance is None:
        raise AttributeError(_('tagged_object must be called with a valid tag'))
    
    queryset = TaggedItem.objects.filter(tag = tag_instance)
    if related_tags:
        related_tags_list = \
            Tag.objects.related_for_model(tag_instance, queryset, counts = related_tag_counts)
    else:
        related_tags_list = []
        
    return queryset, related_tags_list

def parse_tag_input_local(input, max_count = 5):
    """
    Given a list of comma separated tags, return the parsed tags as a list.  Maximum
    max_count tags returned.
    """
    words = parse_tag_input(input)
    words = [word.replace(' ', '-') for word in words][0:max_count]
    return words

def add_tags(object, input):
    """
    Parses the list of comma separated tags in input and associates them with the object.
    """
    tags = parse_tag_input_local(input, 1000)
    for tag in tags:
        Tag.objects.add_tag(object, tag)
    return tags