from django.contrib import admin
from .models import Quiz, Question, Choice, Participation, ParticipationChoice

# TODO: improve admin panel usability, e.g. by showing the questions and choices along with the quizzes

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Participation)
admin.site.register(ParticipationChoice)
