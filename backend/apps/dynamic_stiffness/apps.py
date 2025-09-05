from django.apps import AppConfig


class DynamicStiffnessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dynamic_stiffness'
    verbose_name = '动刚度查询'
