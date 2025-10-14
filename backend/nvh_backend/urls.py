"""
URL configuration for nvh_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static


def health_check(request):
    """简单的健康检查接口"""
    return JsonResponse({'status': 'ok', 'message': 'NVH Backend is running'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('api/users/', include('apps.users.urls')),
    path('api/modal/', include('apps.modal.urls')),
    path('api/sound-insulation/', include('apps.sound_module.urls')),
    path('api/dynamic-stiffness/', include('apps.dynamic_stiffness.urls')),
    path('api/wheel-performance/', include('apps.wheel_performance.urls')),
    path('api/NTF/', include('apps.NTF.urls')),
    path('api/acoustic-analysis/', include('apps.acoustic_analysis.urls')),
    path('api/experience/', include('apps.experience.urls')),
    path('oidc/', include('mozilla_django_oidc.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

