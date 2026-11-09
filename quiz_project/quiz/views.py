from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .form import RegisterForm, QuizForm, QuestionForm
from .models import Quiz, Question, Choice, Attempt, AttemptAnswer

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        user.email = form.cleaned_data["email"]
        user.first_name = form.cleaned_data["first_name"]
        user.save()
        login(request, user)
        messages.success(request, "Your account was created successfully.")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})

@login_required
def dashboard(request):
    search = request.GET.get("q", "").strip()
    quizzes = Quiz.objects.filter(is_active=True)
    if search:
        quizzes = quizzes.filter(Q(title__icontains=search) | Q(category__icontains=search))
    attempts = Attempt.objects.filter(user=request.user).select_related("quiz")[:5]
    return render(request, "quiz/dashboard.html", {
        "quizzes": quizzes, "attempts": attempts, "search": search,
        "total_quizzes": Quiz.objects.filter(is_active=True).count(),
        "total_attempts": Attempt.objects.filter(user=request.user).count(),
    })

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
    questions = quiz.questions.prefetch_related("choices")
    return render(request, "quiz/quiz_detail.html", {"quiz": quiz, "questions": questions})

@login_required
@require_POST
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
    questions = list(quiz.questions.prefetch_related("choices"))
    if not questions:
        messages.error(request, "This quiz does not have any questions yet.")
        return redirect("dashboard")

    total = sum(q.marks for q in questions)
    attempt = Attempt.objects.create(user=request.user, quiz=quiz, total_marks=total)
    score = 0
    for question in questions:
        selected_id = request.POST.get(f"question_{question.id}")
        selected = Choice.objects.filter(pk=selected_id, question=question).first() if selected_id else None
        correct = bool(selected and selected.is_correct)
        if correct:
            score += question.marks
        AttemptAnswer.objects.create(
            attempt=attempt, question=question, selected_choice=selected, is_correct=correct
        )
    attempt.score = score
    attempt.save(update_fields=["score"])
    return redirect("result", attempt_id=attempt.id)

@login_required
def result(request, attempt_id):
    attempt = get_object_or_404(Attempt.objects.select_related("quiz"), pk=attempt_id, user=request.user)
    answers = attempt.answers.select_related("question", "selected_choice").prefetch_related("question__choices")
    return render(request, "quiz/result.html", {"attempt": attempt, "answers": answers})

@login_required
def my_results(request):
    attempts = Attempt.objects.filter(user=request.user).select_related("quiz")
    return render(request, "quiz/my_results.html", {"attempts": attempts})

def staff_required(view):
    return login_required(user_passes_test(lambda u: u.is_staff)(view))

@staff_required
def manage_quizzes(request):
    quizzes = Quiz.objects.all()
    search = request.GET.get("q", "").strip()
    if search:
        quizzes = quizzes.filter(Q(title__icontains=search) | Q(category__icontains=search))
    return render(request, "quiz/manage_quizzes.html", {"quizzes": quizzes, "search": search})

@staff_required
def quiz_create(request):
    form = QuizForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        quiz = form.save(commit=False)
        quiz.created_by = request.user
        quiz.save()
        messages.success(request, "Quiz created. Add questions to complete it.")
        return redirect("question_create", quiz_id=quiz.id)
    return render(request, "quiz/quiz_form.html", {"form": form, "heading": "Create quiz"})

@staff_required
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    form = QuizForm(request.POST or None, instance=quiz)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Quiz updated.")
        return redirect("manage_quizzes")
    return render(request, "quiz/quiz_form.html", {"form": form, "heading": "Edit quiz"})

@staff_required
@require_POST
def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    quiz.delete()
    messages.success(request, "Quiz deleted.")
    return redirect("manage_quizzes")

@staff_required
def question_list(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    return render(request, "quiz/question_list.html", {"quiz": quiz, "questions": quiz.questions.all()})

@staff_required
def question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    form = QuestionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(quiz)
        messages.success(request, "Question added.")
        return redirect("question_list", quiz_id=quiz.id)
    return render(request, "quiz/question_form.html", {"form": form, "quiz": quiz, "heading": "Add question"})

@staff_required
def question_edit(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    form = QuestionForm(request.POST or None, instance=question)
    if request.method == "POST" and form.is_valid():
        form.save(question.quiz)
        messages.success(request, "Question updated.")
        return redirect("question_list", quiz_id=question.quiz.id)
    return render(request, "quiz/question_form.html", {"form": form, "quiz": question.quiz, "heading": "Edit question"})

@staff_required
@require_POST
def question_delete(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    quiz_id = question.quiz_id
    question.delete()
    messages.success(request, "Question deleted.")
    return redirect("question_list", quiz_id=quiz_id)
