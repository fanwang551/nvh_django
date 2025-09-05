from django.urls import path
from . import views

urlpatterns = [
    # 级联查询接口
    path('part-names/', views.get_part_names, name='get_part_names'),
    path('subsystems/', views.get_subsystems, name='get_subsystems'),
    path('test-points/', views.get_test_points, name='get_test_points'),
    
    # 动刚度数据查询接口
    path('data/', views.dynamic_stiffness_query, name='dynamic_stiffness_query'),
]
