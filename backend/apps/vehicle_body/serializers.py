from rest_framework import serializers
from .models import SampleInfo, Substance, SubstancesTestDetail


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


class SubstanceSerializer(serializers.ModelSerializer):
    """物质库序列化器（vehicle_body ）"""
    limit_value_display = serializers.SerializerMethodField()
    class Meta:
        model = Substance
        fields = [
            'id', 'substance_name_cn', 'substance_name_en', 'cas_no',
            'odor_threshold', 'organic_threshold', 'limit_value', 'limit_value_display',
            'odor_character', 'main_usage', 'remark'
        ]

    def get_limit_value_display(self, obj):
        """处理限值显示逻辑"""
        if obj.limit_value == 99999:
            return '无'
        return obj.limit_value if obj.limit_value is not None else '-'

class SubstancesTestDetailSerializer(serializers.ModelSerializer):
    """全谱检测明细序列化器（按 Sample 聚合，无主表）"""
    # 前端期望：substance 字段点击传参，这里直接返回 CAS 号，便于以 cas_no 查询详情
    substance = serializers.CharField(source='substance.cas_no', read_only=True)
    substance_name_cn = serializers.CharField(source='substance.substance_name_cn', read_only=True)
    substance_name_en = serializers.CharField(source='substance.substance_name_en', read_only=True)
    cas_no = serializers.CharField(source='substance.cas_no', read_only=True)
    substance_info = SubstanceSerializer(source='substance', read_only=True)

    match_degree_formatted = serializers.SerializerMethodField()
    retention_time_formatted = serializers.SerializerMethodField()
    concentration_ratio_formatted = serializers.SerializerMethodField()
    concentration_formatted = serializers.SerializerMethodField()

    class Meta:
        model = SubstancesTestDetail
        fields = [
            'id', 'substance', 'substance_name_cn', 'substance_name_en', 'cas_no',
            'substance_info', 'retention_time', 'retention_time_formatted',
            'match_degree', 'match_degree_formatted', 'concentration', 'concentration_formatted',
            'concentration_ratio', 'concentration_ratio_formatted',
            'qij', 'wih'
        ]

    def get_match_degree_formatted(self, obj):
        if obj.match_degree is not None and obj.match_degree != '':
            # 如果 match_degree 已经包含 %，直接返回；否则添加 %
            return obj.match_degree if '%' in obj.match_degree else f"{obj.match_degree}%"
        return None

    def get_retention_time_formatted(self, obj):
        return f"{obj.retention_time:.4f}" if obj.retention_time is not None else None

    def get_concentration_ratio_formatted(self, obj):
        return f"{obj.concentration_ratio:.3f}" if obj.concentration_ratio is not None else None

    def get_concentration_formatted(self, obj):
        return f"{obj.concentration:.3f}" if obj.concentration is not None else None


class SubstancesTestListItemSerializer(serializers.ModelSerializer):
    """前端测试列表项（以 SampleInfo 作为一条测试记录）"""
    sample_info = serializers.SerializerMethodField()

    class Meta:
        model = SampleInfo
        fields = ['id', 'test_date', 'sample_info']

    def get_sample_info(self, obj: SampleInfo):
        # 仅返回项目名称等简化字段，移除冗余的 vehicle_model 兼容结构
        return {
            'project_name': obj.project_name,
            'part_name': obj.part_name,
            'development_stage': obj.development_stage,
            'status': obj.status,
            'test_order_no': obj.test_order_no,
            'sample_no': obj.sample_no,
            # 返回图片访问路径，避免将二进制内容序列化为 JSON
            'sample_image_url': obj.sample_image_url.url if getattr(obj, 'sample_image_url', None) else None,
        }
