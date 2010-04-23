import unittest

from django.contrib.auth.models import User
from tagging.models import Tag, TaggedItem
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
import django_metatagging.utils as utils

class Tests(unittest.TestCase):
    def setUp(self):
        try:
            test_object_1 = User.objects.get(username = 'Test User')
        except ObjectDoesNotExist:
            test_object_1 = User.objects.create_user(username = 'Test User',
                                                     email = 'test_user@gmail.com')
        self.test_object_1 = test_object_1
        
        try:
            test_object_2 = User.objects.get(username = 'Test User 2')
        except ObjectDoesNotExist:
            test_object_2 = User.objects.create_user(username = 'Test User 2',
                                                     email = 'test_user2@gmail.com')
        self.test_object_2 = test_object_2
        
        try:
            test_object_3 = User.objects.get(username = 'Test User 3')
        except ObjectDoesNotExist:
            test_object_3 = User.objects.create_user(username = 'Test User 3',
                                                     email = 'test_user3@gmail.com')
        self.test_object_3 = test_object_3
        
        tags_list = ['Django', 'Python', 'PHP', 'Javascript', 'JQuery']
        for tag in tags_list:
            Tag.objects.add_tag(self.test_object_1, tag)
            if tag in ['Django', 'Python']:
                Tag.objects.add_tag(self.test_object_2, tag)
            if tag == 'Django':
                Tag.objects.add_tag(self.test_object_3, tag)
        self.standard_tags = tags_list
        self.tags = Tag.objects.all()
        self.tagged_items = TaggedItem.objects.all()
        
    def tearDown(self):
        self.test_object_1.delete()
        self.test_object_2.delete()
        self.test_object_3.delete()
        for tag in self.tags:
            tag.delete()
        for tagged_item in self.tagged_items:
            tagged_item.delete()
            
    def test_most_active(self):
        """
        Tests retrieval of the most active Tags.
        """
        content_type_id = ContentType.objects.get_for_model(User).id
        active_tags = Tag.meta_objects.most_active(content_type_id, 10)
        self.assertEqual('Django', active_tags[0].name)
        self.assertEqual('Python', active_tags[1].name)
    
    def test_count_tags(self):
        """
        Tests retrieving a queryset of Tags with their associated 
        count of TaggedItem objects.
        """
        tags_with_count = Tag.meta_objects.count_tags(self.tags.order_by('name'))
        self.assertEqual(3, tags_with_count[0].count)
        self.assertEqual(2, tags_with_count[4].count)
    
    def test_retag(self):
        """
        Tests retagging an object with a new list of tags.
        """
        new_tags = ['Diablo', 'Mephisto', 'Baal']
        current_tags, final_tags = Tag.meta_objects.retag(self.test_object_1, new_tags)
        final_tags = Tag.objects.get_for_object(self.test_object_1)
        self.assertEqual([x.name for x in final_tags], sorted(new_tags))
        self.assertEqual(current_tags, sorted(self.standard_tags))
        Tag.meta_objects.retag(self.test_object_1, self.standard_tags)
        
    def test_related_for_tags(self):
        """
        Tests MetaTagManager.related_for_tags.
        """
        related_tags = Tag.meta_objects.related_for_tags(['Django'])
        self.assertEqual(sorted(['Python', 'PHP', 'Javascript', 'JQuery']), [x.name for x in related_tags])
    
    def test_parse_local(self):
        """
        Tests django_metatagging.utils.parse_local_input.
        """
        starting_words = ",".join(['django metatagging', 'abcdefg', 'u s a', 'a', 'b', 'c', 'd'])
        final_words = utils.parse_tag_input_local(starting_words, 5)
        self.assertEqual(5, len(final_words))
        self.assertFalse('django-metatagging' in final_words)
        self.assertFalse('u-s-a' in final_words)
    
    def test_add_tags(self):
        """
        Tests add a list of tags to an object.
        """
        starting_words = ",".join(['django metatagging', 'abcdefg', 'u s a', 'a', 'b', 'c', 'd'])
        utils.add_tags(self.test_object_1, starting_words)
        final_tags = Tag.objects.get_for_object(self.test_object_1)
        self.assertTrue('django-metatagging' in [x.name for x in final_tags])
        self.assertTrue('u-s-a' in [x.name for x in final_tags])
        Tag.meta_objects.retag(self.test_object_1, self.standard_tags)