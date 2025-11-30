from django.urls import path
from . import views


urlpatterns = [
    path('home/', views.home_dashboard, name='nvh_home_dashboard'),
]

