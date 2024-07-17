from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Quiz, Question, Choice, Participation, ParticipationChoice


class QuizTests(APITestCase):
    # TODO: add more comprehensive tests (aim for >90% code coverage)
    def setUp(self):
        self.user_creator = User.objects.create_user(username='creator', password='password')
        self.user_participant = User.objects.create_user(username='participant', password='password')

        self.quiz_data = {
            "title": "Sample Quiz",
            "questions": [
                {
                    "text": "Sample Question 1",
                    "choices": [
                        {"text": "Choice 1", "is_correct": True},
                        {"text": "Choice 2", "is_correct": False}
                    ]
                },
                {
                    "text": "Sample Question 2",
                    "choices": [
                        {"text": "Choice A", "is_correct": False},
                        {"text": "Choice B", "is_correct": True}
                    ]
                }
            ]
        }

    def test_unauthorized_quiz_creation(self):
        response = self.client.post(reverse('quiz_create'), self.quiz_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_quiz_creation(self):
        self.client.login(username='creator', password='password')

        response = self.client.post(reverse('quiz_create'), self.quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(Question.objects.count(), 2)
        self.assertEqual(Choice.objects.count(), 4)

    def test_quiz_retrieval(self):
        self.client.login(username='creator', password='password')
        quiz = Quiz.objects.create(creator=self.user_creator, title='Sample Quiz')

        response = self.client.get(reverse('quiz_detail', kwargs={'pk': quiz.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Sample Quiz')

    def test_participate_in_quiz(self):
        self.client.login(username='participant', password='password')

        quiz = Quiz.objects.create(creator=self.user_creator, title='Sample Quiz')
        question = Question.objects.create(quiz=quiz, text='Sample Question')
        choice = Choice.objects.create(question=question, text='Choice 1', is_correct=True)

        participation_data = {
            'quiz': quiz.id,
            'choices': [{'question_id': question.id, 'choice_id': choice.id}]
        }

        response = self.client.post(reverse('quiz_participate', kwargs={'pk': quiz.id}), participation_data,
                                    format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 100)

        self.assertEqual(Participation.objects.count(), 1)
        self.assertEqual(ParticipationChoice.objects.count(), 1)

    def test_retrieve_relevant_quizzes(self):
        self.client.login(username='participant', password='password')

        quiz = Quiz.objects.create(creator=self.user_creator, title='Sample Quiz')
        Participation.objects.create(user=self.user_participant, quiz=quiz, score=1)

        response = self.client.get(reverse('quiz_relevant_to_user'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['created']), 0)

        self.assertEqual(len(response.data['participated']), 1)
        self.assertEqual(response.data['participated'][0]['title'], 'Sample Quiz')

    def test_quiz_results_view_participant(self):
        self.client.login(username='participant', password='password')

        quiz = Quiz.objects.create(creator=self.user_creator, title='Sample Quiz')
        question = Question.objects.create(quiz=quiz, text='Sample Question')
        choice = Choice.objects.create(question=question, text='Choice 1', is_correct=True)

        # Simulate a user participation
        participation = Participation.objects.create(user=self.user_participant, quiz=quiz, score=100)
        ParticipationChoice.objects.create(participation=participation, selected_choice=choice)

        response = self.client.get(reverse('quiz_results', kwargs={'pk': quiz.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['participant_score'], 100)
        self.assertEqual(response.data['participants_count'], 1)

    def test_quiz_results_view_creator(self):
        self.client.login(username='creator', password='password')

        quiz = Quiz.objects.create(creator=self.user_creator, title='Sample Quiz')
        question = Question.objects.create(quiz=quiz, text='Sample Question')
        choice = Choice.objects.create(question=question, text='Choice 1', is_correct=True)

        participation = Participation.objects.create(user=self.user_participant, quiz=quiz, score=100)
        ParticipationChoice.objects.create(participation=participation, selected_choice=choice)

        response = self.client.get(reverse('quiz_results', kwargs={'pk': quiz.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['participants_count'], 1)
        self.assertEqual(response.data['choices_with_result_by_question'],
                         {1: [{'id': 1, 'text': 'Choice 1', 'is_correct': True}]})
        self.assertEqual(response.data['participations'][0]['selected_choices'], [{'selected_choice': 1}])
