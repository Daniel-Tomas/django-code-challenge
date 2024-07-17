from rest_framework import serializers
from .models import Quiz, Question, Choice, Participation, ParticipationChoice


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text']


class CreatorChoiceSerializer(ChoiceSerializer):
    class Meta(ChoiceSerializer.Meta):
        fields = ChoiceSerializer.Meta.fields + ['is_correct']


class CreatorQuestionSerializer(serializers.ModelSerializer):
    choices = CreatorChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']


class CreatorQuizSerializer(serializers.ModelSerializer):
    questions = CreatorQuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'is_open', 'creator', 'created_at', 'questions']
        read_only_fields = ['creator']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')

        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions_data:
            choices_data = question_data.pop('choices')

            question = Question.objects.create(quiz=quiz, **question_data)

            for choice_data in choices_data:
                Choice.objects.create(question=question, **choice_data)

        return quiz


class QuestionSerializer(CreatorQuestionSerializer):
    choices = ChoiceSerializer(many=True)


class QuizSerializer(CreatorQuizSerializer):
    questions = QuestionSerializer(many=True)


class QuizRelevantToMeSerializer(serializers.ModelSerializer):
    """Whether the title should be included depends on how this API is to be used, on how the UI is designed"""

    class Meta:
        model = Quiz
        fields = ['id', 'title']


class ParticipationChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipationChoice
        fields = ['selected_choice']


class ParticipationSerializer(serializers.ModelSerializer):
    selected_choices = ParticipationChoiceSerializer(many=True)

    class Meta:
        model = Participation
        fields = ['id', 'user', 'score', 'created_at', 'selected_choices']
