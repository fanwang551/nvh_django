from django.urls import path
from . import views

urlpatterns = [
    # VOC数据接口
    path('data/', views.voc_data_list, name='voc_data_list'),
    path('statistics/', views.voc_statistics, name='voc_statistics'),
    path('chart-data/', views.voc_chart_data, name='voc_chart_data'),
    path('row-chart-data/', views.voc_row_chart_data, name='voc_row_chart_data'),
    path('odor-row-chart-data/', views.odor_row_chart_data, name='odor_row_chart_data'),
    
    # 选项接口
    path('options/part-names/', views.part_name_options, name='part_name_options'),
    path('options/vehicle-models/', views.vehicle_model_options, name='vehicle_model_options'),
    path('options/status/', views.status_options, name='status_options'),
    path('options/development-stages/', views.development_stage_options, name='development_stage_options'),
]
