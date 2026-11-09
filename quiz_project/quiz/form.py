from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Quiz, Question


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ("first_name", "username", "email", "password1", "password2")


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ["title", "description", "category", "duration_minutes", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "duration_minutes": forms.NumberInput(attrs={"min": 1}),
        }


class QuestionForm(forms.ModelForm):
    choice_1 = forms.CharField(label="Option A", max_length=300)
    choice_2 = forms.CharField(label="Option B", max_length=300)
    choice_3 = forms.CharField(label="Option C", max_length=300)
    choice_4 = forms.CharField(label="Option D", max_length=300)
    correct_choice = forms.ChoiceField(
        choices=[
            ("1", "Option A"),
            ("2", "Option B"),
            ("3", "Option C"),
            ("4", "Option D"),
        ],
        widget=forms.RadioSelect,
        label="Correct answer",
    )

    class Meta:
        model = Question
        fields = ["text", "marks", "order"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 2}),
            "marks": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            choices = list(self.instance.choices.all().order_by("id"))
            for index, choice in enumerate(choices[:4], start=1):
                self.fields[f"choice_{index}"].initial = choice.text
                if choice.is_correct:
                    self.fields["correct_choice"].initial = str(index)

    def save(self, quiz, commit=True):
        question = super().save(commit=False)
        question.quiz = quiz
        question.save()
        question.choices.all().delete()
        correct = self.cleaned_data["correct_choice"]
        for index in range(1, 5):
            from .models import Choice

            Choice.objects.create(
                question=question,
                text=self.cleaned_data[f"choice_{index}"],
                is_correct=(str(index) == correct),
            )
        return question
