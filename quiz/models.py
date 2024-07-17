from django.db import models
from django.contrib.auth.models import User


class Quiz(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    is_open = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "quizzes"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)

    text = models.TextField()


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)

    text = models.TextField()
    is_correct = models.BooleanField(default=False)


class Participation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    score = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)


class ParticipationChoice(models.Model):
    participation = models.ForeignKey(Participation, related_name='selected_choices', on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
