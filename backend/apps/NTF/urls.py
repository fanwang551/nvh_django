from django.urls import path

from apps.NTF import views

urlpatterns = [
    path('infos/', views.ntf_info_list, name='ntf-info-list'),
    path('infos/<int:pk>/', views.ntf_info_detail, name='ntf-info-detail'),
    path('infos/by-vehicle/<int:vehicle_id>/', views.ntf_info_by_vehicle, name='ntf-info-by-vehicle'),
]

