from rest_framework import serializers
from .models import SampleInfo


class SampleInfoSerializer(serializers.ModelSerializer):
    """样品信息序列化器（新schema）"""

    class Meta:
        model = SampleInfo
        fields = [
            'id', 'project_name', 'part_name', 'development_stage', 'status',
            'test_order_no', 'sample_no', 'sample_image_url', 'test_date',
            # VOC
            'benzene', 'toluene', 'ethylbenzene', 'xylene', 'styrene',
            'formaldehyde', 'acetaldehyde', 'acrolein', 'acetone', 'tvoc',
            # 气味
            'odor_static_front', 'odor_static_rear', 'odor_dynamic_front',
            'odor_dynamic_rear', 'odor_mean'
        ]


class VocOdorDataSerializer(serializers.ModelSerializer):
    """与旧前端兼容的扁平结构 + 格式化字段"""
    sample_info = SampleInfoSerializer(source='*', read_only=True)

    # VOC格式化
    benzene_formatted = serializers.SerializerMethodField()
    toluene_formatted = serializers.SerializerMethodField()
    ethylbenzene_formatted = serializers.SerializerMethodField()
    xylene_formatted = serializers.SerializerMethodField()
    styrene_formatted = serializers.SerializerMethodField()
    formaldehyde_formatted = serializers.SerializerMethodField()
    acetaldehyde_formatted = serializers.SerializerMethodField()
    acrolein_formatted = serializers.SerializerMethodField()
    acetone_formatted = serializers.SerializerMethodField()
    tvoc_formatted = serializers.SerializerMethodField()

    # 气味格式化
    static_front = serializers.DecimalField(source='odor_static_front', max_digits=6, decimal_places=1, required=False, allow_null=True)
    static_rear = serializers.DecimalField(source='odor_static_rear', max_digits=6, decimal_places=1, required=False, allow_null=True)
    dynamic_front = serializers.DecimalField(source='odor_dynamic_front', max_digits=6, decimal_places=1, required=False, allow_null=True)
    dynamic_rear = serializers.DecimalField(source='odor_dynamic_rear', max_digits=6, decimal_places=1, required=False, allow_null=True)
    odor_mean_formatted = serializers.SerializerMethodField()
    static_front_formatted = serializers.SerializerMethodField()
    static_rear_formatted = serializers.SerializerMethodField()
    dynamic_front_formatted = serializers.SerializerMethodField()
    dynamic_rear_formatted = serializers.SerializerMethodField()

    class Meta:
        model = SampleInfo
        fields = [
            'id',
            # 根层透出 test_date 以兼容旧表格列
            'test_date',
            # VOC 原值 + 格式化
            'benzene', 'toluene', 'ethylbenzene', 'xylene', 'styrene',
            'formaldehyde', 'acetaldehyde', 'acrolein', 'acetone', 'tvoc',
            'benzene_formatted', 'toluene_formatted', 'ethylbenzene_formatted',
            'xylene_formatted', 'styrene_formatted', 'formaldehyde_formatted',
            'acetaldehyde_formatted', 'acrolein_formatted', 'acetone_formatted', 'tvoc_formatted',
            # 气味 原值(字段名沿用旧前端) + 格式化
            'static_front', 'static_rear', 'dynamic_front', 'dynamic_rear',
            'odor_mean', 'odor_mean_formatted',
            'static_front_formatted', 'static_rear_formatted',
            'dynamic_front_formatted', 'dynamic_rear_formatted',
            # 嵌套样品信息（含project_name等）
            'sample_info'
        ]

    # ---- VOC formatted helpers ----
    def _fmt3(self, v):
        return f"{v:.3f}" if v is not None else None

    def get_benzene_formatted(self, obj):
        return self._fmt3(obj.benzene)

    def get_toluene_formatted(self, obj):
        return self._fmt3(obj.toluene)

    def get_ethylbenzene_formatted(self, obj):
        return self._fmt3(obj.ethylbenzene)

    def get_xylene_formatted(self, obj):
        return self._fmt3(obj.xylene)

    def get_styrene_formatted(self, obj):
        return self._fmt3(obj.styrene)

    def get_formaldehyde_formatted(self, obj):
        return self._fmt3(obj.formaldehyde)

    def get_acetaldehyde_formatted(self, obj):
        return self._fmt3(obj.acetaldehyde)

    def get_acrolein_formatted(self, obj):
        return self._fmt3(obj.acrolein)

    def get_acetone_formatted(self, obj):
        return self._fmt3(getattr(obj, 'acetone', None))

    def get_tvoc_formatted(self, obj):
        return self._fmt3(obj.tvoc)

    # ---- Odor formatted helpers ----
    def _fmt1(self, v):
        return f"{v:.1f}" if v is not None else None

    def get_static_front_formatted(self, obj):
        return self._fmt1(obj.odor_static_front)

    def get_static_rear_formatted(self, obj):
        return self._fmt1(obj.odor_static_rear)

    def get_dynamic_front_formatted(self, obj):
        return self._fmt1(obj.odor_dynamic_front)

    def get_dynamic_rear_formatted(self, obj):
        return self._fmt1(obj.odor_dynamic_rear)

    def get_odor_mean_formatted(self, obj):
        return self._fmt1(obj.odor_mean)

