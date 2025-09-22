from django.urls import path

from apps.wheel_performance import views

urlpatterns = [
    path('', views.wheel_performance_list, name='wheel-performance-list'),
    path('<int:pk>/', views.wheel_performance_detail, name='wheel-performance-detail'),
]
