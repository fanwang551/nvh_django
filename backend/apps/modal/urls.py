from django.urls import path
from . import views

urlpatterns = [
    # 车型相关接口
    path('vehicle-models/', views.vehicle_model_list, name='vehicle_model_list'),
    
    # 零件相关接口
    path('components/', views.component_list, name='component_list'),
    path('components/from-test-projects/', views.testproject_component_list, name='testproject_component_list'),
    
    # 模态数据相关接口
    path('modal-data/', views.modal_data_query, name='modal_data_query'),
    path('modal-data/statistics/', views.modal_data_statistics, name='modal_data_statistics'),

    # 模态数据对比相关接口
    path('modal-data/compare/', views.modal_data_compare, name='modal_data_compare'),
    path('modal-data/related-vehicles/', views.get_related_vehicle_models, name='get_related_vehicle_models'),
    path('modal-data/test-statuses/', views.get_test_statuses, name='get_test_statuses'),
    path('modal-data/mode-types/', views.get_mode_types, name='get_mode_types'),
    
    # 新增接口
    path('modal-data/all-test-statuses/', views.get_all_test_statuses, name='get_all_test_statuses'),
    path('modal-data/mode-types-by-component/', views.get_mode_types_by_component, name='get_mode_types_by_component'),

    # 气密性测试相关接口
    path('airtightness-data/compare/', views.airtightness_data_compare, name='airtightness_data_compare'),
    path('airtightness-images/', views.airtightness_images_query, name='airtightness_images_query'),
]
