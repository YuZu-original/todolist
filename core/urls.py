from django.urls import path

from core import views

urlpatterns = [
    path("signup", views.SignupView.as_view()),
    path("login", views.LoginView.as_view()),
]