from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("quiz/<int:quiz_id>/", views.quiz_detail, name="quiz_detail"),
    path("quiz/<int:quiz_id>/submit/", views.submit_quiz, name="submit_quiz"),
    path("result/<int:attempt_id>/", views.result, name="result"),
    path("my-results/", views.my_results, name="my_results"),
    path("manage/quizzes/", views.manage_quizzes, name="manage_quizzes"),
    path("manage/quizzes/create/", views.quiz_create, name="quiz_create"),
    path("manage/quizzes/<int:quiz_id>/edit/", views.quiz_edit, name="quiz_edit"),
    path("manage/quizzes/<int:quiz_id>/delete/", views.quiz_delete, name="quiz_delete"),
    path("manage/quizzes/<int:quiz_id>/questions/", views.question_list, name="question_list"),
    path("manage/quizzes/<int:quiz_id>/questions/add/", views.question_create, name="question_create"),
    path("manage/questions/<int:question_id>/edit/", views.question_edit, name="question_edit"),
    path("manage/questions/<int:question_id>/delete/", views.question_delete, name="question_delete"),
]
