from django.urls import path
from . import views

urlpatterns = [
    # 隔声区域相关接口
    path('areas/', views.sound_insulation_area_list, name='sound_insulation_area_list'),

    # 车型相关接口
    path('vehicles/', views.get_vehicles_by_area, name='get_vehicles_by_area'),

    # 隔声量对比相关接口
    path('compare/', views.sound_insulation_compare, name='sound_insulation_compare'),

    # 车型隔声量相关接口
    path('vehicle-sound-data/', views.get_vehicles_with_sound_data, name='get_vehicles_with_sound_data'),
    path('vehicle-sound-compare/', views.vehicle_sound_insulation_compare, name='vehicle_sound_insulation_compare'),
]
