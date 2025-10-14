from rest_framework import serializers
from .models import Experience, default_media


def _normalize_media(value):
    if value in (None, ""):
        return default_media()
    if isinstance(value, dict):
        images = value.get('images') or []
        videos = value.get('videos') or []
        if not isinstance(images, list) or not isinstance(videos, list):
            raise serializers.ValidationError('媒体字段必须包含 images、videos 数组')
        return {"images": images, "videos": videos}
    raise serializers.ValidationError('媒体字段必须为对象')


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'


class ExperienceCreateUpdateSerializer(serializers.ModelSerializer):
    problem_media = serializers.JSONField(required=False, allow_null=True)
    analysis_media = serializers.JSONField(required=False, allow_null=True)
    solution_media = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = Experience
        fields = (
            'id', 'category', 'problem_name', 'keywords', 'description',
            'problem_media', 'analysis_content', 'analysis_media',
            'solution_content', 'solution_media', 'creator'
        )

    def validate_problem_media(self, value):
        return _normalize_media(value)

    def validate_analysis_media(self, value):
        return _normalize_media(value)

    def validate_solution_media(self, value):
        return _normalize_media(value)

