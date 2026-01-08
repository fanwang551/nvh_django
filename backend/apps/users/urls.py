from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('info/', views.user_info, name='user_info'),
    path('profile/', views.user_profile, name='user_profile'),
    path('groups/', views.user_groups, name='user_groups'),
    path('auth-test/', views.auth_test, name='auth_test'),
]
