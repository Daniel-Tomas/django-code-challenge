from collections import defaultdict

from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Quiz, Choice, Participation, ParticipationChoice
from .serializers import QuizSerializer, ParticipationSerializer, CreatorQuizSerializer, QuizRelevantToMeSerializer, \
    CreatorChoiceSerializer


class QuizCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreatorQuizSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class QuizDetailView(RetrieveAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    permission_classes = [IsAuthenticated]


class QuizRelevantToUserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        created_quizzes = Quiz.objects.filter(creator=request.user)
        participated_quizzes = Quiz.objects.filter(participation__user=request.user)

        data = {
            'created': QuizRelevantToMeSerializer(created_quizzes, many=True).data,
            'participated': QuizRelevantToMeSerializer(participated_quizzes, many=True).data
        }

        return Response(data)


class QuizResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
         - Response to the creator: participants count, correct choices,
           selected choices and scores for every user who has participated
         - Response to the rest of users: if already participated, participants count and the participant's score
           (we could let the participants see all the results as well, it would depend on the requirements)
         """

        quiz = get_object_or_404(Quiz, id=pk)
        participations = Participation.objects.filter(quiz=quiz)

        participants_count = {'participants_count': participations.count()}

        # ------- Response to the rest of users -------
        if request.user != quiz.creator:
            participant = participations.filter(user=request.user).first()
            if participant:
                return Response({**participants_count,
                                 'participant_score': participant.score})

            if quiz.is_open:
                return Response({'detail': 'Participate first to be able to see the results'},
                                status=status.HTTP_403_FORBIDDEN)

            return Response(
                {'detail': 'Results unavailable: user has not participated on the quiz and the quiz is already closed'},
                status=status.HTTP_403_FORBIDDEN)
        # ---------------------------------------------

        # ------- Response to the creator -------
        participations_data = ParticipationSerializer(participations, many=True).data

        choices_with_result_by_question = {}
        for question in quiz.questions.all():
            choices_with_result_by_question[question.id] = CreatorChoiceSerializer(question.choices.all(),
                                                                                   many=True).data

        quiz_results = {
            **participants_count,
            'participations': participations_data,
            'choices_with_result_by_question': choices_with_result_by_question
        }

        return Response(quiz_results)
        # ---------------------------------------


class QuizParticipateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Anyone authenticated can participate in a quiz if the quiz id is known (e.g. sent from creator via a link)"""
        quiz = get_object_or_404(Quiz, id=pk)

        # ------ base cases, validations ------
        if not quiz.is_open:
            return Response({'detail': 'Quiz is closed'}, status=status.HTTP_403_FORBIDDEN)

        if request.user == quiz.creator:
            return Response({'detail': 'Quiz creator cannot participate on his own quiz'},
                            status=status.HTTP_403_FORBIDDEN)

        if Participation.objects.filter(user=request.user, quiz=quiz).exists():
            return Response({'detail': 'User already participated on quiz'}, status=status.HTTP_403_FORBIDDEN)
        # -------------------------------------

        choice_ids = [choice_data['choice_id'] for choice_data in request.data['choices']]
        selected_choices = get_list_or_404(Choice, id__in=choice_ids)

        score = self._calculate_score(quiz, selected_choices)

        participation = Participation.objects.create(user=request.user, quiz=quiz, score=score)
        for selected_choice in selected_choices:
            ParticipationChoice.objects.create(participation=participation, selected_choice=selected_choice)

        return Response({'score': participation.score}, status=status.HTTP_201_CREATED)

    @staticmethod
    def _calculate_score(quiz, selected_choices):
        # TODO: improve the scoring algorithm, e.g. by reducing points for incorrectly selected choices

        selected_choices_by_question = defaultdict(list)
        for choice in selected_choices:
            selected_choices_by_question[choice.question].append(choice)

        all_questions_score = 0
        for question in quiz.questions.all():
            correct_selected_choices_count = sum(
                1 for choice in selected_choices_by_question[question] if choice.is_correct)

            all_correct_choices_count = sum(1 for choice in question.choices.all() if choice.is_correct)

            if all_correct_choices_count > 0:
                all_questions_score += correct_selected_choices_count / all_correct_choices_count

        questions_count = quiz.questions.count()
        all_questions_avg_score = (all_questions_score / questions_count) * 100 if questions_count > 0 else 0

        return all_questions_avg_score
