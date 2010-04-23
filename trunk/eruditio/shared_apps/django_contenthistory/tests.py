import unittest
import imp
try:
    import json
except:
    import simplejson as json

from django.contrib.auth.models import User
from django_contenthistory.models import TrackedContent, ModelHistory, ModelField
from django.contrib.contenttypes.models import ContentType
import django_contenthistory.utils as utils
from django.core.exceptions import ObjectDoesNotExist

class Tests(unittest.TestCase):
    def setUp(self):
        try:
            tracked_content = TrackedContent.objects.get(content_type = ContentType.objects.get_for_model(User))
        except ObjectDoesNotExist:
            tracked_content = TrackedContent(content_type = ContentType.objects.get_for_model(User))
            tracked_content.save()
        
        try:
            test_user = User.objects.get(username = 'Test User')
        except ObjectDoesNotExist:
            test_user = User(username = 'Test User')
            test_user.save()
            
        self.test_user = test_user
        self.tracked_content = tracked_content
        self.tracked_contents = TrackedContent.objects.all()
        
    def tearDown(self):
        for tracked_content in self.tracked_contents:
            tracked_content.delete()
        self.test_user.delete()
        
    def test_model_registration(self):
        """
        Tests registration of post_save signals with the correct handlers for each TrackedContent
        in the database.
        """
        import django_contenthistory.handlers as handlers
        handlers = imp.new_module('handlers')
        import django_contenthistory.contenthistory
        
        django_contenthistory.contenthistory.content_history = django_contenthistory.contenthistory.ContentHistory()
        
        for tracked_content in self.tracked_contents:
            content_name = "%s_%s" % (tracked_content.content_type.app_label, tracked_content.content_type.model)
            self.assertEqual(django_contenthistory.contenthistory.content_history._registry[content_name], tracked_content.content_type)
    
    def test_associate_revision_fields(self):
        """
        Determines if the correct fields are being associated correctly with an edit.
        """
        target_field = ModelField(name = 'username', mode = ModelField.TEXT, content = self.tracked_content)
        target_field.save()
        model_history = ModelHistory(object_id = self.test_user.id, 
                                     content_type = ContentType.objects.get_for_model(User),
                                     created = False,
                                     data = json.dumps({'username':'hanbox'}),
                                     user = self.test_user)
        final_edit = utils.associate_revision_fields(model_history)
        self.assertTrue(final_edit.fields)
        self.assertEqual(final_edit.fields[0]['name'], 'username')
        self.assertEqual(final_edit.fields[0]['content'], 'hanbox')
        target_field.delete()
    
    def test_base_handler(self):
        """
        Tests the standard handler for data handling and tracked content
        registration.
        """
        from django_contenthistory.handlers import BaseHistoryHandler
        
        handler = BaseHistoryHandler(ContentType.objects.get_for_model(User))
        current_user = User(username = 'genghisu')
        final_user = User(username = 'hanbox')
        target_field = ModelField(name = 'username', mode = ModelField.TEXT, content = self.tracked_content)
        target_field.save()
        created, object_id, data, modified = handler.get_data(current_user, final_user)
        self.assertTrue(modified)
        self.assertFalse(created)
        self.assertEqual(json.loads(data).get('username'), utils.generate_diff('genghisu', 'hanbox'))
        target_field.delete()
        
    def test_unchanged_data(self):
        """
        Test to determine if correct value is generated if a field has not changed.
        """
        from django_contenthistory.handlers import BaseHistoryHandler
        
        handler = BaseHistoryHandler(ContentType.objects.get_for_model(User))
        current_user = User(username = 'hanbox')
        final_user = User(username = 'hanbox')
        target_field = ModelField(name = 'username', mode = ModelField.TEXT, content = self.tracked_content)
        target_field.save()
        created, object_id, data, modified = handler.get_data(current_user, final_user)
        self.assertFalse(modified)
        self.assertFalse(created)
        target_field.delete()