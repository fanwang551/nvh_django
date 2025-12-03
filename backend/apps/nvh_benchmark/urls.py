from django.urls import path

from . import views

urlpatterns = [
    path('vehicle-models/', views.list_vehicle_models, name='nvh-benchmark-vehicle-models'),
    path('overview/', views.get_benchmark_overview, name='nvh-benchmark-overview'),
]
