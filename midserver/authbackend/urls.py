from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.UserSignup.as_view()),
    path('login/', views.UserLogin.as_view()),
    path('logout/', views.UserLogout.as_view()),
    path('getcsrftoken/', views.GetCSRFToken.as_view()),
    path('get_authstatus/', views.CheckAuthenticated.as_view()),
    path('get_user_email', views.GetUserEmail.as_view()),
]




