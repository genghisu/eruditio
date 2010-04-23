import unittest

from django.contrib.auth.models import User
from django_moderation.models import (ModeratedContent, ContentFlag, ContentFlagSet,
                                      ContentFlagSetMember, ContentFlagInstance,
                                      ContentFlagVote, ContentApprovalVote,
                                      Reason)
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

class ModerationTests(unittest.TestCase):
    def setUp(self):
        try:
            moderated_content = ModeratedContent.objects.get(content_type = ContentType.objects.get_for_model(User))
        except ObjectDoesNotExist:
            moderated_content = ModeratedContent(content_type = ContentType.objects.get_for_model(User),
                                                 accept_threshold = 100,
                                                 reject_threshold = 100)
            moderated_content.save()
        
        try:
            test_user = User.objects.get(username = 'test_user')
        except ObjectDoesNotExist:
            test_user = test_user = User.objects.create_user(username = 'test_user',
                                                             email = 'test_user@test.com',
                                                             password = None)
        self.test_user = test_user
        self.moderated_content = moderated_content
        self.moderated_contents = ModeratedContent.objects.all()
    
    def tearDown(self):
        from django_moderation.moderation import moderation
        
        self.moderated_content.delete()
        self.test_user.delete()
        moderation.unregister(ContentType.objects.get_for_model(User))
    
    def test_moderation_registration(self):
        """
        Tests registration of Badge handlers found in handlers.py.
        """
        from django_moderation.moderation import moderation
        
        self.assertEqual(moderation._registry.get(User._meta.db_table, None), ContentType.objects.get_for_model(User))
        
class ContentApprovalTests(unittest.TestCase):
    def setUp(self):
        try:
            test_user = User.objects.get(username = 'test_user')
        except ObjectDoesNotExist:
            test_user = test_user = User.objects.create_user(username = 'test_user',
                                                             email = 'test_user@test.com',
                                                             password = None)
        self.test_user = test_user
        
        try:
            test_user_2 = User.objects.get(username = 'test_user_2')
        except ObjectDoesNotExist:
            test_user_2 = test_user = User.objects.create_user(username = 'test_user_2',
                                                               email = 'test_user@test.com',
                                                               password = None)
        self.user = test_user_2
        
        try:
            moderated_content = ModeratedContent.objects.get(content_type = ContentType.objects.get_for_model(User))
        except ObjectDoesNotExist:
            moderated_content = ModeratedContent(content_type = ContentType.objects.get_for_model(User),
                                                 accept_threshold = 100,
                                                 reject_threshold = 100)
            moderated_content.save()
        self.moderated_content = moderated_content
        
    def tearDown(self):
        self.test_user.delete()
        self.user.delete()
        self.moderated_content.delete()
    
    def test_queue_for_moderation(self):
        """
        Tests putting an object into the moderation queue.
        """
        ContentApprovalVote.objects.queue_for_moderation(self.test_user)
        
        self.assertTrue(ContentFlag.objects.flags_for_object(self.test_user))
        for flag in ContentFlag.objects.flags_for_object(self.test_user):
            flag.delete()
    
    def test_vote(self):
        """
        Tests adding an accept, pass or reject vote to an object in
        moderation.
        """ 
        status = ContentApprovalVote.objects.vote(self.user, self.user, ContentApprovalVote.ACCEPT)
        self.assertTrue(status)
        for vote in ContentApprovalVote.objects.all():
            vote.delete()
            
    def test_can_vote(self):
        """
        Tests ContentApprovalManager.can_vote.
        """
        can_vote = ContentApprovalVote.objects.can_vote(self.user, self.user)
        self.assertTrue(can_vote)
        status = ContentApprovalVote.objects.vote(self.user, self.user, ContentApprovalVote.ACCEPT)
        self.assertTrue(status)
        can_vote = ContentApprovalVote.objects.can_vote(self.user, self.user)
        self.assertFalse(can_vote)
        for vote in ContentApprovalVote.objects.all():
            vote.delete()

    def test_check_threshold(self):
        """
        Tests threshold check which determines if an object in the moderation queue gets
        accepted or rejected.
        """
        status = ContentApprovalVote.objects.vote(self.user, self.user, ContentApprovalVote.ACCEPT)
        check_status = ContentApprovalVote.objects.check_threshold(self.user)
        self.assertTrue(check_status)
        
    def test_queue(self):
        """
        Tests object retrieval to fill the moderation queue.
        """
        ContentApprovalVote.objects.queue_for_moderation(self.test_user)
        instance = ContentApprovalVote.objects.queue(self.test_user)
        self.assertEqual(instance.content_object, self.test_user)
        
class ContentFlagTests(unittest.TestCase):
    def setUp(self):
        try:
            test_user = User.objects.get(username = 'test_user')
        except ObjectDoesNotExist:
            test_user = test_user = User.objects.create_user(username = 'test_user',
                                                             email = 'test_user@test.com',
                                                             password = None)
        self.test_user = test_user
        self.user = test_user
        
        try:
            moderation_flag = ContentFlag.objects.get(name = ContentFlag.MODERATE_FLAG)
        except ObjectDoesNotExist:
            moderation_flag = ContentFlag(name = ContentFlag.MODERATE_FLAG,
                                          active = True,
                                          description = '')
            moderation_flag.save()
        self.moderation_flag = moderation_flag
        
        try:
            accept_flag = ContentFlag.objects.get(name = ContentFlag.ACCEPT_FLAG)
        except ObjectDoesNotExist:
            accept_flag = ContentFlag(name = ContentFlag.ACCEPT_FLAG,
                                      active = True,
                                      description = '')
            accept_flag.save()
        self.accept_flag = accept_flag
        
        try:
            reject_flag = ContentFlag.objects.get(name = ContentFlag.REJECT_FLAG)
        except ObjectDoesNotExist:
            reject_flag = ContentFlag(name = ContentFlag.REJECT_FLAG,
                                      active = True,
                                      description = '')
            reject_flag.save()
        self.reject_flag = reject_flag
        
        self.flags = [moderation_flag, accept_flag, reject_flag]
        
        try:
            moderation_flag_set = ContentFlagSet.objects.get(name = 'moderation')
        except ObjectDoesNotExist:
            moderation_flag_set = ContentFlagSet(name = 'moderation',
                                                 exclusive = True,
                                                 active = True)
            moderation_flag_set.save()
        self.moderation_flag_set = moderation_flag_set
        
        for flag in self.flags:
            flag_member_instance = ContentFlagSetMember(set = moderation_flag_set,
                                                        flag = flag)
            flag_member_instance.save()
        
        try:
            test_flag = ContentFlag.objects.get(name = 'test')
        except ObjectDoesNotExist:
            test_flag = ContentFlag(name = 'test',
                                    active = True,
                                    description = '')
            test_flag.save()
        self.test_flag = test_flag
        
    def tearDown(self):
        self.test_user.delete()
        self.moderation_flag.delete()
        self.accept_flag.delete()
        self.reject_flag.delete()
        self.test_flag.delete()
        self.moderation_flag_set.delete()
        
    def test_has_flag(self):
        """
        Tests ContentFlagManager checking of flag existense on an object.
        """
        flag_instance = ContentFlag.objects.add_flag(self.user, self.moderation_flag)
        self.assertTrue(ContentFlag.objects.has_flag(self.user, ContentFlag.MODERATE_FLAG))
        flag_instance.delete()
    
    def test_add_flag(self):
        """
        Tests adding flags to objects.
        """
        flag_instance = ContentFlag.objects.add_flag(self.user, self.moderation_flag)
        self.assertTrue(ContentFlag.objects.has_flag(self.user, ContentFlag.MODERATE_FLAG))
        flag_instance.delete()
        
    def test_remove_flag(self):
        """
        Tests removing flags from objects.
        """
        flag_instance = ContentFlag.objects.add_flag(self.user, self.moderation_flag)
        final_flag_instance = ContentFlag.objects.remove_flag(self.user, self.moderation_flag)
        self.assertFalse(ContentFlag.objects.has_flag(self.user, ContentFlag.MODERATE_FLAG))
    
    def test_exclude_for_set(self):
        """
        Tests exlusive sets of flags working correctly when added and removed.
        """
        flag_instance_1 = ContentFlag.objects.add_flag(self.user, self.moderation_flag)
        self.assertTrue(ContentFlag.objects.has_flag(self.user, ContentFlag.MODERATE_FLAG))
        flag_instance_2 = ContentFlag.objects.add_flag(self.user, self.accept_flag)
        self.assertFalse(ContentFlag.objects.has_flag(self.user, ContentFlag.MODERATE_FLAG))
        self.assertTrue(ContentFlag.objects.has_flag(self.user, ContentFlag.ACCEPT_FLAG))
        flag_instance_1.delete()
        flag_instance_2.delete()
        
    def test_objects_with_flag(self):
        """
        Tests retrieval of all objects with a particular flag.
        """
        flag_instance = ContentFlag.objects.add_flag(self.user, self.moderation_flag)
        objects_with_moderation_flag = ContentFlag.objects.objects_with_flag(self.moderation_flag)
        self.assertEqual(len(objects_with_moderation_flag), 1)
        self.assertEqual(objects_with_moderation_flag[0].content_object, self.user)
        flag_instance.delete()
        
    def test_flags_for_object(self):
        """
        Tests retrieval of all flags for a target object.
        """
        flag_instance = ContentFlag.objects.add_flag(self.user, self.moderation_flag)
        flags_for_object = ContentFlag.objects.flags_for_object(self.user)
        self.assertTrue(len(flags_for_object), 1)
        self.assertEqual(flag_instance, flags_for_object[0])

    def test_add_flag_vote(self):
        """
        Tests adding a ContentFlagVote to an object.
        """
        content_type_id = ContentType.objects.get_for_model(User).id
        object_id = self.user.id
        flag = self.test_flag
        reason = Reason(name = 'test',
                        description = '')
        reason.save()
        details = 'Testing flag vote instance.'
        flag_vote = ContentFlagVote.objects.add_vote(content_type_id = content_type_id,
                                                     object_id = object_id,
                                                     flag = flag.name,
                                                     reason = reason.name,
                                                     details = details,
                                                     user = self.user
                                                     )
        self.assertTrue(flag_vote)
        self.assertEqual(flag_vote.additional_info, details)
        self.assertTrue(flag_vote.user, self.user)
        self.assertTrue(flag_vote.reason, reason)
        flag_vote.delete()
        reason.delete()
    
class ManagerTests(unittest.TestCase):
    def setUp(self):
        try:
            moderated_content = ModeratedContent.objects.get(content_type = ContentType.objects.get_for_model(User))
        except ObjectDoesNotExist:
            moderated_content = ModeratedContent(content_type = ContentType.objects.get_for_model(User),
                                                 accept_threshold = 100,
                                                 reject_threshold = 100)
            moderated_content.save()
            
        try:
            test_user = User.objects.get(username = 'test_user')
        except ObjectDoesNotExist:
            test_user = test_user = User.objects.create_user(username = 'test_user',
                                                             email = 'test_user@test.com',
                                                             password = None)
        self.test_user = test_user
        self.user = test_user
        self.moderated_content = moderated_content
        self.moderated_contents = ModeratedContent.objects.all()
        
        try:
            accept_flag = ContentFlag.objects.get(name = ContentFlag.ACCEPT_FLAG)
        except ObjectDoesNotExist:
            accept_flag = ContentFlag(name = ContentFlag.ACCEPT_FLAG,
                                      active = True,
                                      description = '')
            accept_flag.save()
        self.accept_flag = accept_flag
    
        try:
            hidden_flag = ContentFlag.objects.get(name = ContentFlag.HIDDEN_FLAG)
        except ObjectDoesNotExist:
            hidden_flag = ContentFlag(name = ContentFlag.HIDDEN_FLAG,
                                      active = True,
                                      description = '')
            hidden_flag.save() 
        self.hidden_flag = hidden_flag
        
    def tearDown(self):
        self.test_user.delete()
        self.accept_flag.delete()
        self.hidden_flag.delete()
        self.moderated_content.delete()
    
    def test_moderated_content_manager(self):
        """
        Tests django_moderation.managers.ModeratedContentManager.
        """
        from django_moderation.managers import ModeratedContentManager
        
        User.moderated_objects = ModeratedContentManager()
        User.moderated_objects.model = User
        self.assertFalse(User.moderated_objects.all())
        flag_instance = ContentFlag.objects.add_flag(self.user, self.accept_flag)
        self.assertTrue(User.moderated_objects.all())
    
    def test_hidden_content_manager(self):
        """
        Tests django_moderation.managers.HiddenContentManager.
        """
        from django_moderation.managers import HiddenContentManager
        
        User.hidden_objects = HiddenContentManager()
        User.hidden_objects.model = User
        self.assertTrue(User.hidden_objects.all())
        flag_instance = ContentFlag.objects.add_flag(self.user, self.hidden_flag)
        self.assertFalse(User.hidden_objects.all())