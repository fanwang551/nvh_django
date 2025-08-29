from django.urls import path
from . import views

urlpatterns = [
    # 车型相关接口
    path('vehicle-models/', views.vehicle_model_list, name='vehicle_model_list'),
    
    # 零件相关接口
    path('components/', views.component_list, name='component_list'),
    
    # 模态数据相关接口
    path('modal-data/', views.modal_data_query, name='modal_data_query'),
    path('modal-data/statistics/', views.modal_data_statistics, name='modal_data_statistics'),
]
