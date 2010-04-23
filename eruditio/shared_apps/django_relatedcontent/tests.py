import unittest

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
import django_relatedcontent.utils as utils
from django_relatedcontent.models import (All, AvailableContentUsage, ContentUsage,
                                          ContentAssociation)
from django.core.exceptions import ObjectDoesNotExist

class Tests(unittest.TestCase):
    def setUp(self):
        try:
            user_1 = User.objects.get(username = 'Test User')
        except ObjectDoesNotExist:
            user_1 = User.objects.create_user(username = 'Test User',
                                              email = 'test_user@gmail.com')
        self.user_1 = user_1
        
        try:
            user_2 = User.objects.get(username = 'Test User 2')
        except ObjectDoesNotExist:
            user_2 = User.objects.create_user(username = 'Test User 2',
                                              email = 'test_user2@gmail.com')
        self.user_2 = user_2
        
        try:
            standard_usage = ContentUsage.objects.get(name = 'standard')
        except ObjectDoesNotExist:
            standard_usage = ContentUsage(name = 'standard')
            standard_usage.save()
        self.usage = standard_usage
        self.standard_usage = standard_usage
        
        test_usages = []
        for i in range(1, 6):
            new_usage, created = ContentUsage.objects.get_or_create(name = 'Test Usage %s' % str(i))
            test_usages.append(new_usage)
        self.test_usages = test_usages
        available_usage = AvailableContentUsage(usage = standard_usage,
                                                base_model = ContentType.objects.get_for_model(User),
                                                selectable_model = ContentType.objects.get_for_model(ContentUsage))
        available_usage.save()
        self.available_usage = available_usage
        
    def tearDown(self):
        self.user_1.delete()
        self.user_2.delete()
        self.standard_usage.delete()
        self.available_usage.delete()
        for usage in self.test_usages:
            usage.delete()
        for association in ContentAssociation.objects.all():
            association.delete()
            
    def test_usage_for_base_content_type(self):
        """
        Tests retrieval of AvailableUsages associated with a base
        content type.
        """
        usages = ContentUsage.objects.usage_for_base_content_type(ContentType.objects.get_for_model(User).id, self.standard_usage)
        self.assertTrue(usages)
        self.assertEqual(usages[0], self.available_usage)
        
    def test_add_association(self):
        """
        Tests adding an association between a base content object
        and a selectable content object.
        """
        user_content_type = ContentType.objects.get_for_model(User)
        usage_content_type = ContentType.objects.get_for_model(ContentUsage)
        association = ContentAssociation.objects.add_association(base_content_type = user_content_type,
                                                                 base_object_id = self.user_1.id,
                                                                 selectable_content_type = usage_content_type,
                                                                 selectable_object_id = self.usage.id,
                                                                 usage = self.usage)
        self.assertTrue(association)
        self.assertTrue(ContentAssociation.objects.associations_for_object(self.user_1, self.usage))
        
    def test_remove_association(self):
        """
        Tests removing an association between two objects.
        """
        user_content_type = ContentType.objects.get_for_model(User)
        usage_content_type = ContentType.objects.get_for_model(ContentUsage)
        association = ContentAssociation.objects.add_association(base_content_type = user_content_type,
                                                                 base_object_id = self.user_1.id,
                                                                 selectable_content_type = usage_content_type,
                                                                 selectable_object_id = self.usage.id,
                                                                 usage = self.usage)
        self.assertTrue(association)
        self.assertTrue(ContentAssociation.objects.associations_for_object(self.user_1, self.standard_usage))
        ContentAssociation.objects.remove_association(base_content_type = user_content_type,
                                                      base_object_id = self.user_1.id,
                                                      selectable_content_type = usage_content_type,
                                                      selectable_object_id = self.usage.id,
                                                      usage = self.usage)
        self.assertFalse(ContentAssociation.objects.associations_for_object(self.user_1, self.standard_usage))
    
    def test_add_associations(self):
        """
        Tests adding multiple associations at once.
        """
        usage_content_type_id = ContentType.objects.get_for_model(ContentUsage).id
        data = ",".join(["(%s %s)" % (str(usage_content_type_id), x.id) for x in self.test_usages])
        associations = ContentAssociation.objects.add_associations(self.user_1, self.usage, data)
        final_associations = ContentAssociation.objects.associations_for_object(self.user_1, self.usage)
        self.assertTrue(len(final_associations), 5)
        self.assertTrue(len(associations), 5)
        
    def test_associations_for_object(self):
        """
        Tests retrieval of all associations with the object
        being the base object.
        """
        user_content_type = ContentType.objects.get_for_model(User)
        usage_content_type = ContentType.objects.get_for_model(ContentUsage)
        association = ContentAssociation.objects.add_association(base_content_type = user_content_type,
                                                                 base_object_id = self.user_1.id,
                                                                 selectable_content_type = usage_content_type,
                                                                 selectable_object_id = self.usage.id,
                                                                 usage = self.usage)
        final_associations = ContentAssociation.objects.associations_for_object(self.user_1, self.usage)
        self.assertTrue(final_associations)
        self.assertEqual(final_associations[0].usage, self.usage)
        self.assertEqual(final_associations[0].parent, self.user_1)
    
    def test_get_max_usage_count(self):
        """
        Tests retrieving the max usage count associated with a target
        object.
        """
        user_content_type = ContentType.objects.get_for_model(User)
        usage_content_type_id = ContentType.objects.get_for_model(ContentUsage).id
        data = ",".join(["(%s %s)" % (str(usage_content_type_id), x.id) for x in self.test_usages])
        associations = ContentAssociation.objects.add_associations(self.user_1, self.usage, data)
        final_associations = ContentAssociation.objects.associations_for_object(self.user_1, self.usage)
        max_usage_count = ContentAssociation.objects.get_max_usage_count(user_content_type,
                                                                         self.user_1.id,
                                                                         self.usage)
        self.assertEqual(max_usage_count, 5)
        
    def test_parse_relatedcontent_data(self):
        """
        Tests parsing of related content data.
        """
        data = "(1 1), (2 2), (3 3)"
        final_data = utils.parse_relatedcontent_data(data)
        self.assertEqual(len(final_data), 3)
        self.assertTrue(('1', '1') in final_data)
        self.assertTrue(('2', '2') in final_data)
        self.assertTrue(('3', '3') in final_data)
    
class DummyRequest(object):
    def __init__(self):
        self.META = {'ip':'192.168.1.1'}
        self.GET = {'target_id':'TARGET',
                    'data_id':'DATA',
                    'mode':'MODE',
                    'ajax_associate_url':'AJAX_URL'}
        
class ChangeListTests(unittest.TestCase):
    def setUp(self):
        try:
            user_1 = User.objects.get(username = 'Test User')
        except ObjectDoesNotExist:
            user_1 = User.objects.create_user(username = 'Test User',
                                              email = 'test_user@gmail.com')
        self.user_1 = user_1
        
        try:
            standard_usage = ContentUsage.objects.get(name = 'standard')
        except ObjectDoesNotExist:
            standard_usage = ContentUsage(name = 'standard')
            standard_usage.save()
        self.usage = standard_usage
        
        change_list = utils.SelectChangeList(User, self.user_1.id, ContentUsage, self.usage, DummyRequest())
        self.change_list = change_list
        
        test_usages = []
        for i in range(1, 6):
            new_usage = ContentUsage(name = 'Test Usage %s' % str(i))
            new_usage.save()
            test_usages.append(new_usage)
        self.test_usages = test_usages
        
    def tearDown(self):
        self.user_1.delete()
        for usage in self.test_usages:
            usage.delete()
            
    def test_parse_query_params(self):
        """
        Tests parsing of query parameters from the request.
        """
        params = self.change_list.parse_query_params()
        self.assertTrue(params)
        self.assertEqual(params['target_id'], 'TARGET')
        self.assertEqual(params['data_id'], 'DATA')
        self.assertEqual(params['mode'], 'form/js')
        self.assertEqual(params['ajax_associate_url'], '')
    
    def test_check_mode(self):
        """
        Tests mode checking to ensure that a valid mode
        is being used.
        """
        params = self.change_list.parse_query_params()
        status = self.change_list.check_mode()
        self.assertTrue(status)
    
    def test_get_related_objects(self):
        """
        Tests retrieval of all related objects associated
        with the base object.
        """
        usage_content_type_id = ContentType.objects.get_for_model(ContentUsage).id
        data = ",".join(["(%s %s)" % (str(usage_content_type_id), x.id) for x in self.test_usages])
        associations = ContentAssociation.objects.add_associations(self.user_1, self.usage, data)
        related_objects = self.change_list.get_related_objects()
        self.assertEqual(len(related_objects), 5)