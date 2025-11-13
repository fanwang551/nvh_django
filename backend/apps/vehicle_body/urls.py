from django.urls import path
from . import views

urlpatterns = [
    path('iaq-dashboard/', views.iaq_dashboard, name='vehicle_body_iaq_dashboard'),
    path('data/', views.data_list, name='vehicle_body_data_list'),
    path('options/vehicle-models/', views.project_name_options, name='vehicle_body_project_name_options'),
    path('row-chart-data/', views.row_chart_data, name='vehicle_body_row_chart_data'),
    path('odor-row-chart-data/', views.odor_row_chart_data, name='vehicle_body_odor_row_chart_data'),
    path('filtered-voc-chart-data/', views.filtered_voc_chart_data, name='vehicle_body_filtered_voc_chart_data'),
    path('filtered-odor-chart-data/', views.filtered_odor_chart_data, name='vehicle_body_filtered_odor_chart_data'),
    # 贡献度TOP25
    path('contribution-top25/', views.contribution_top25, name='vehicle_body_contribution_top25'),
    # 全谱物质接口
    path('substances/test-list/', views.substances_test_list, name='vehicle_body_substances_test_list'),
    path('substances/test-detail/', views.substances_test_detail, name='vehicle_body_substances_test_detail'),
    path('substances/substance-detail/', views.substance_detail, name='vehicle_body_substance_detail'),
    # 污染物分项溯源接口
    path('substance-traceability/vehicle-sample-options/', views.vehicle_sample_options, name='vehicle_body_vehicle_sample_options'),
    path('substance-traceability/substances/', views.traceability_substances, name='vehicle_body_traceability_substances'),
    path('substance-traceability/ranking/', views.traceability_ranking, name='vehicle_body_traceability_ranking'),
]
