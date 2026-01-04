from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# ViewSets will be registered in Task 3/3

urlpatterns = [
    path('', include(router.urls)),
]
