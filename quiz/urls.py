from django.urls import path

from quiz.views import QuizCreateView, QuizParticipateView, QuizResultsView, QuizDetailView, QuizRelevantToUserListView

urlpatterns = [
    path('quizzes/', QuizCreateView.as_view(), name='quiz_create'),

    path('quizzes/relevant-to-me/', QuizRelevantToUserListView.as_view(), name='quiz_relevant_to_user'),

    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz_detail'),

    path('quizzes/<int:pk>/results/', QuizResultsView.as_view(), name='quiz_results'),

    path('quizzes/<int:pk>/participate/', QuizParticipateView.as_view(), name='quiz_participate'),
]
