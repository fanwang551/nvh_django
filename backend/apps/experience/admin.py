from django.contrib import admin
from .models import Experience


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'category', 'problem_name', 'creator', 'create_time'
    )
    search_fields = (
        'problem_name', 'keywords', 'description', 'category', 'creator'
    )
    list_filter = ('category',)

