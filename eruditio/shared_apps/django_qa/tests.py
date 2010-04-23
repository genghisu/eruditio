import unittest

from django.contrib.auth.models import User
from django_qa.models import Question, Answer
from django.core.exceptions import ObjectDoesNotExist

class Tests(unittest.TestCase):
    def setUp(self):
        try:
            test_user = User.objects.get(username = 'Test User')
        except ObjectDoesNotExist:
            test_user = User.objects.create_user(username = 'Test User',
                                                 email = 'test_user@gmail.com')
        self.user = test_user
        
        try:
            test_user_1 = User.objects.get(username = 'Test User 2')
        except ObjectDoesNotExist:
            test_user_1 = User.objects.create_user(username = 'Test User 2',
                                                   email = 'test_user2@gmail.com')
        self.test_user = test_user_1
        
    def tearDown(self):
        self.user.delete()
        self.test_user.delete()
        for question in Question.objects.all():
            question.delete()
            
    def test_ask_question(self):
        """
        Tests asking a question.
        """
        data = {'title':'Test Question',
                'question':'Testing Questions Yo.'}
        new_question = Question.objects.add(self.user, data)
        self.assertTrue(new_question)
        self.assertEqual(new_question.question, data.get('question'))
        self.assertEqual(new_question.user, self.user)
        self.assertEqual(new_question.name, data.get('title'))
        
    def test_answer_question(self):
        """
        Tests answering a question.
        """
        question_data = {'title':'Test Question',
                'question':'Testing Questions Yo.'}
        new_question = Question.objects.add(self.test_user, question_data)
        new_answer = Answer.objects.answer_question('Test Answer', new_question, self.user)
        self.assertTrue(new_answer)
        self.assertEqual(new_answer.question, new_question)
        self.assertEqual(new_answer.answer, 'Test Answer')
        
    def test_edit_question(self):
        """
        Tests editing a question.
        """
        question_data = {'title':'Test Question',
                         'question':'Testing Questions Yo.'}
        new_question = Question.objects.add(self.test_user, question_data)
        edit_data = {'title':'Edit Question',
                     'question':'Editing Questions Yo.'}
        modified_question = Question.objects.edit(new_question, self.user, edit_data)
        self.assertTrue(modified_question)
        self.assertEqual(modified_question.question, edit_data.get('question'))
        self.assertEqual(modified_question.user, self.test_user)
        self.assertEqual(modified_question.name, edit_data.get('title'))
        
    def test_edit_answer(self):
        """
        Tests editing an answer.
        """
        data = {'title':'Test Question',
                'question':'Testing Questions Yo.'}
        new_question = Question.objects.add(self.user, data)
        new_answer = Answer.objects.answer_question('Test Answer', new_question, self.user)
        modified_answer = Answer.objects.edit(new_answer, self.user, {'answer':'Edit Answer'})
        self.assertTrue(modified_answer)
        self.assertEqual(modified_answer.question, new_question)
        self.assertEqual(modified_answer.answer, 'Edit Answer')
        
    def test_accept_answer(self):
        """
        Tests accepting an answer.
        """
        data = {'title':'Test Question',
                'question':'Testing Questions Yo.'}
        new_question = Question.objects.add(self.user, data)
        new_answer = Answer.objects.answer_question('Test Answer', new_question, self.user)
        Question.objects.accept_answer(new_answer)
        self.assertEqual(new_answer, Question.objects.get_accepted_answer(new_question))
    