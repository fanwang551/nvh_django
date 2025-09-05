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

    # 车辆混响时间相关接口
    path('vehicle-reverberation-data/', views.get_vehicles_with_reverberation_data, name='get_vehicles_with_reverberation_data'),
    path('vehicle-reverberation-compare/', views.vehicle_reverberation_compare, name='vehicle_reverberation_compare'),

    # 吸声系数相关接口
    path('sound-absorption/part-names/', views.get_part_name_options, name='get_part_name_options'),
    path('sound-absorption/material-compositions/', views.get_material_composition_options, name='get_material_composition_options'),
    path('sound-absorption/weights/', views.get_weight_options, name='get_weight_options'),
    path('sound-absorption/query/', views.sound_absorption_query, name='sound_absorption_query'),

    # 隔声量系数相关接口
    path('sound-insulation-coefficient/test-types/', views.get_test_type_options, name='get_test_type_options'),
    path('sound-insulation-coefficient/part-names/', views.get_insulation_part_name_options, name='get_insulation_part_name_options'),
    path('sound-insulation-coefficient/material-compositions/', views.get_insulation_material_composition_options, name='get_insulation_material_composition_options'),
    path('sound-insulation-coefficient/weights/', views.get_insulation_weight_options, name='get_insulation_weight_options'),
    path('sound-insulation-coefficient/query/', views.sound_insulation_coefficient_query, name='sound_insulation_coefficient_query'),

    # 材料孔隙率流阻相关接口
    path('material-porosity/part-names/', views.get_material_porosity_part_names, name='get_material_porosity_part_names'),
    path('material-porosity/query/', views.material_porosity_query, name='material_porosity_query'),
]
