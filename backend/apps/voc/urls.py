from django.urls import path
from . import views

urlpatterns = [
    # VOC数据接口
    path('data/', views.voc_data_list, name='voc_data_list'),
    path('statistics/', views.voc_statistics, name='voc_statistics'),
    path('chart-data/', views.voc_chart_data, name='voc_chart_data'),
    path('row-chart-data/', views.voc_row_chart_data, name='voc_row_chart_data'),
    path('odor-row-chart-data/', views.odor_row_chart_data, name='odor_row_chart_data'),
    path('filtered-voc-chart-data/', views.filtered_voc_chart_data, name='filtered_voc_chart_data'),
    path('filtered-odor-chart-data/', views.filtered_odor_chart_data, name='filtered_odor_chart_data'),
    
    # 选项接口
    path('options/part-names/', views.part_name_options, name='part_name_options'),
    path('options/vehicle-models/', views.vehicle_model_options, name='vehicle_model_options'),
    path('options/status/', views.status_options, name='status_options'),
    path('options/development-stages/', views.development_stage_options, name='development_stage_options'),
    
    # 全谱检测接口
    path('substances/test-list/', views.substances_test_list, name='substances_test_list'),
    path('substances/test-detail/', views.substances_test_detail, name='substances_test_detail'),
    path('substances/substance-detail/', views.substance_detail, name='substance_detail'),

    # 贡献度TOP25接口
    path('contribution-top25/', views.contribution_top25, name='contribution_top25'),
    
    # 物质分项溯源接口
    path('substances/item-traceability/', views.substance_item_traceability, name='substance_item_traceability'),
]
