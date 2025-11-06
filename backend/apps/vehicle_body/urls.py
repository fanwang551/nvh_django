from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.data_list, name='vehicle_body_data_list'),
    path('options/vehicle-models/', views.project_name_options, name='vehicle_body_project_name_options'),
    path('row-chart-data/', views.row_chart_data, name='vehicle_body_row_chart_data'),
    path('odor-row-chart-data/', views.odor_row_chart_data, name='vehicle_body_odor_row_chart_data'),
    path('filtered-voc-chart-data/', views.filtered_voc_chart_data, name='vehicle_body_filtered_voc_chart_data'),
    path('filtered-odor-chart-data/', views.filtered_odor_chart_data, name='vehicle_body_filtered_odor_chart_data'),
]

