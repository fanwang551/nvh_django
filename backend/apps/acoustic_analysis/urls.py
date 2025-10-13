from django.urls import path

from apps.acoustic_analysis import views

urlpatterns = [
    path('work-conditions/', views.get_work_conditions, name='acoustic-work-conditions'),
    path('measure-points/', views.get_measure_points, name='acoustic-measure-points'),
    path('query/', views.query_acoustic_data, name='acoustic-query'),
]

