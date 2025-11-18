from django.urls import path

from apps.acoustic_analysis import views

urlpatterns = [
    path('work-conditions/', views.get_work_conditions, name='acoustic-work-conditions'),
    path('measure-points/', views.get_measure_points, name='acoustic-measure-points'),
    path('query/', views.query_acoustic_data, name='acoustic-query'),
    path('steady-state/query/', views.query_steady_state_data, name='steady-state-query'),
    path('dynamic/work-conditions/', views.get_dynamic_work_conditions, name='dynamic-work-conditions'),
    path('dynamic/measure-points/', views.get_dynamic_measure_points, name='dynamic-measure-points'),
    path('dynamic/query/', views.query_dynamic_noise, name='dynamic-query'),
    path('dynamic/<int:pk>/spectrum/', views.get_dynamic_spectrum_data, name='dynamic-spectrum-data'),
]
