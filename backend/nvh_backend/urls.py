"""
URL configuration for nvh_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    """简单的健康检查接口"""
    return JsonResponse({'status': 'ok', 'message': 'NVH Backend is running'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('api/users/', include('apps.users.urls')),
    path('api/modal/', include('apps.modal.urls')),
    path('oidc/', include('mozilla_django_oidc.urls')),
]
