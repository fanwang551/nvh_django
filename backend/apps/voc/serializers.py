from rest_framework import serializers
from . import models
from .models import SampleInfo, VocOdorResult
from apps.modal.models import VehicleModel


class VehicleModelSimpleSerializer(serializers.ModelSerializer):
    """车型简单序列化器"""
    class Meta:
        model = VehicleModel
        fields = ['id', 'vehicle_model_name', 'cle_model_code']


class SampleInfoSerializer(serializers.ModelSerializer):
    """样品信息序列化器"""
    vehicle_model = VehicleModelSimpleSerializer(read_only=True)
    vehicle_model_id = serializers.IntegerField(write_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SampleInfo
        fields = [
            'id', 'vehicle_model', 'vehicle_model_id', 'part_name', 
            'development_stage', 'status', 'status_display', 'test_order_no',
            'sample_no', 'sample_image_url'
        ]


class VocOdorResultSerializer(serializers.ModelSerializer):
    """VOC和气味检测结果序列化器"""
    sample_info = SampleInfoSerializer(source='sample', read_only=True)
    
    # 格式化显示保留3位小数（VOC数据）
    benzene_formatted = serializers.SerializerMethodField()
    toluene_formatted = serializers.SerializerMethodField()
    ethylbenzene_formatted = serializers.SerializerMethodField()
    xylene_formatted = serializers.SerializerMethodField()
    styrene_formatted = serializers.SerializerMethodField()
    formaldehyde_formatted = serializers.SerializerMethodField()
    acetaldehyde_formatted = serializers.SerializerMethodField()
    acrolein_formatted = serializers.SerializerMethodField()
    tvoc_formatted = serializers.SerializerMethodField()
    
    # 格式化显示保留1位小数（气味数据）
    static_front_formatted = serializers.SerializerMethodField()
    static_rear_formatted = serializers.SerializerMethodField()
    dynamic_front_formatted = serializers.SerializerMethodField()
    dynamic_rear_formatted = serializers.SerializerMethodField()
    odor_mean_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = VocOdorResult
        fields = [
            'id', 'sample', 'sample_info', 'benzene', 'toluene', 'ethylbenzene', 
            'xylene', 'styrene', 'formaldehyde', 'acetaldehyde', 'acrolein', 'tvoc', 
            'test_date', 'benzene_formatted', 'toluene_formatted', 'ethylbenzene_formatted',
            'xylene_formatted', 'styrene_formatted', 'formaldehyde_formatted', 
            'acetaldehyde_formatted', 'acrolein_formatted', 'tvoc_formatted',
            'static_front', 'static_rear', 'dynamic_front', 'dynamic_rear', 'odor_mean',
            'static_front_formatted', 'static_rear_formatted', 'dynamic_front_formatted',
            'dynamic_rear_formatted', 'odor_mean_formatted'
        ]
    
    def get_benzene_formatted(self, obj):
        return f"{obj.benzene:.3f}" if obj.benzene is not None else None
    
    def get_toluene_formatted(self, obj):
        return f"{obj.toluene:.3f}" if obj.toluene is not None else None
    
    def get_ethylbenzene_formatted(self, obj):
        return f"{obj.ethylbenzene:.3f}" if obj.ethylbenzene is not None else None
    
    def get_xylene_formatted(self, obj):
        return f"{obj.xylene:.3f}" if obj.xylene is not None else None
    
    def get_styrene_formatted(self, obj):
        return f"{obj.styrene:.3f}" if obj.styrene is not None else None
    
    def get_formaldehyde_formatted(self, obj):
        return f"{obj.formaldehyde:.3f}" if obj.formaldehyde is not None else None
    
    def get_acetaldehyde_formatted(self, obj):
        return f"{obj.acetaldehyde:.3f}" if obj.acetaldehyde is not None else None
    
    def get_acrolein_formatted(self, obj):
        return f"{obj.acrolein:.3f}" if obj.acrolein is not None else None
    
    def get_tvoc_formatted(self, obj):
        return f"{obj.tvoc:.3f}" if obj.tvoc is not None else None
    
    def get_static_front_formatted(self, obj):
        return f"{obj.static_front:.1f}" if obj.static_front is not None else None
    
    def get_static_rear_formatted(self, obj):
        return f"{obj.static_rear:.1f}" if obj.static_rear is not None else None
    
    def get_dynamic_front_formatted(self, obj):
        return f"{obj.dynamic_front:.1f}" if obj.dynamic_front is not None else None
    
    def get_dynamic_rear_formatted(self, obj):
        return f"{obj.dynamic_rear:.1f}" if obj.dynamic_rear is not None else None
    
    def get_odor_mean_formatted(self, obj):
        return f"{obj.odor_mean:.1f}" if obj.odor_mean is not None else None


# 保留别名以兼容旧代码
VocResultSerializer = VocOdorResultSerializer


class VocQuerySerializer(serializers.Serializer):
    """VOC查询序列化器"""
    vehicle_model_id = serializers.IntegerField(required=False, allow_null=True)
    part_name = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    test_order_no = serializers.CharField(required=False, allow_blank=True)
    page = serializers.IntegerField(default=1)
    page_size = serializers.IntegerField(default=10)
    
    def validate(self, data):
        # 这里可以添加验证逻辑
        return data


class VocChartDataSerializer(serializers.Serializer):
    """VOC图表数据序列化器"""
    main_group = serializers.CharField()
    sub_group = serializers.CharField()
    benzene = serializers.DecimalField(max_digits=10, decimal_places=4, allow_null=True)
    toluene = serializers.DecimalField(max_digits=10, decimal_places=4, allow_null=True)
    ethylbenzene = serializers.DecimalField(max_digits=10, decimal_places=4, allow_null=True)
    xylene = serializers.DecimalField(max_digits=10, decimal_places=4, allow_null=True)
    styrene = serializers.DecimalField(max_digits=10, decimal_places=4, allow_null=True)
    formaldehyde = serializers.DecimalField(max_digits=10, decimal_places=4, allow_null=True)
    acetaldehyde = serializers.DecimalField(max_digits=10, decimal_places=4, allow_null=True)
    acrolein = serializers.DecimalField(max_digits=10, decimal_places=4, allow_null=True)
    tvoc = serializers.DecimalField(max_digits=10, decimal_places=4, allow_null=True)


class PartNameOptionSerializer(serializers.Serializer):
    """零件名称选项序列化器"""
    value = serializers.CharField()
    label = serializers.CharField()


class VehicleModelOptionSerializer(serializers.Serializer):
    """车型选项序列化器"""
    value = serializers.IntegerField()
    label = serializers.CharField()


class StatusOptionSerializer(serializers.Serializer):
    """状态选项序列化器"""
    value = serializers.CharField()
    label = serializers.CharField()


class SubstanceSerializer(serializers.ModelSerializer):
    """物质库序列化器"""
    class Meta:
        model = models.Substance
        fields = [
            'id', 'substance_name_cn', 'substance_name_en', 'cas_no',
            'odor_threshold', 'organic_threshold', 'limit_value',
            'odor_character', 'main_usage', 'remark'
        ]


class SubstancesTestDetailSerializer(serializers.ModelSerializer):
    """全谱检测明细序列化器"""
    substance_name_cn = serializers.CharField(source='substance.substance_name_cn', read_only=True)
    substance_name_en = serializers.CharField(source='substance.substance_name_en', read_only=True)
    cas_no = serializers.CharField(source='substance.cas_no', read_only=True)
    substance_info = SubstanceSerializer(source='substance', read_only=True)
    
    match_degree_formatted = serializers.SerializerMethodField()
    retention_time_formatted = serializers.SerializerMethodField()
    concentration_ratio_formatted = serializers.SerializerMethodField()
    concentration_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = models.SubstancesTestDetail
        fields = [
            'id', 'substance', 'substance_name_cn', 'substance_name_en', 'cas_no',
            'substance_info', 'retention_time', 'retention_time_formatted',
            'match_degree', 'match_degree_formatted', 'concentration', 'concentration_formatted',
            'concentration_ratio', 'concentration_ratio_formatted',
            'dilution_oij', 'dilution_wih'
        ]
    
    def get_match_degree_formatted(self, obj):
        return f"{obj.match_degree:.2f}%" if obj.match_degree is not None else None
    
    def get_retention_time_formatted(self, obj):
        return f"{obj.retention_time:.4f}" if obj.retention_time is not None else None
    
    def get_concentration_ratio_formatted(self, obj):
        return f"{obj.concentration_ratio:.3f}" if obj.concentration_ratio is not None else None
    
    def get_concentration_formatted(self, obj):
        return f"{obj.concentration:.6f}" if obj.concentration is not None else None


class SubstancesTestSerializer(serializers.ModelSerializer):
    """全谱检测主表序列化器"""
    sample_info = SampleInfoSerializer(source='sample', read_only=True)
    details = SubstancesTestDetailSerializer(many=True, read_only=True)
    
    oi_formatted = serializers.SerializerMethodField()
    goi_formatted = serializers.SerializerMethodField()
    vi_formatted = serializers.SerializerMethodField()
    gvi_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = models.SubstancesTest
        fields = [
            'id', 'sample', 'sample_info', 'oi', 'oi_formatted',
            'goi', 'goi_formatted', 'vi', 'vi_formatted',
            'gvi', 'gvi_formatted', 'test_date', 'details'
        ]
    
    def get_oi_formatted(self, obj):
        return f"{obj.oi:.3f}" if obj.oi is not None else None
    
    def get_goi_formatted(self, obj):
        return f"{obj.goi:.3f}" if obj.goi is not None else None
    
    def get_vi_formatted(self, obj):
        return f"{obj.vi:.3f}" if obj.vi is not None else None
    
    def get_gvi_formatted(self, obj):
        return f"{obj.gvi:.3f}" if obj.gvi is not None else None


class SubstancesQuerySerializer(serializers.Serializer):
    """全谱检测查询序列化器"""
    vehicle_model_id = serializers.IntegerField(required=False, allow_null=True)
    part_name = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    development_stage = serializers.CharField(required=False, allow_blank=True)
    test_order_no = serializers.CharField(required=False, allow_blank=True)
    sample_no = serializers.CharField(required=False, allow_blank=True)
    test_date_start = serializers.DateField(required=False, allow_null=True)
    test_date_end = serializers.DateField(required=False, allow_null=True)
    page = serializers.IntegerField(default=1)
    page_size = serializers.IntegerField(default=10)


class ContributionTop25QuerySerializer(serializers.Serializer):
    """贡献度TOP25查询序列化器"""
    vehicle_model_id = serializers.IntegerField(required=False, allow_null=True)
    vehicle_model_name = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        vm_id = attrs.get('vehicle_model_id')
        vm_name = attrs.get('vehicle_model_name')
        if vm_id is None and not vm_name:
            raise serializers.ValidationError('必须提供vehicle_model_id或vehicle_model_name其一')
        return attrs


class SubstanceItemTraceabilityQuerySerializer(serializers.Serializer):
    """物质分项溯源查询序列化器"""
    vehicle_model_id = serializers.IntegerField(required=True)
    substance_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=False
    )

    def validate(self, attrs):
        vehicle_model_id = attrs.get('vehicle_model_id')
        substance_ids = attrs.get('substance_ids')
        
        if not vehicle_model_id:
            raise serializers.ValidationError('必须提供vehicle_model_id')
        if not substance_ids:
            raise serializers.ValidationError('必须选择至少一种物质')
        
        return attrs


class SubstanceTraceabilityTopSourceSerializer(serializers.Serializer):
    """物质溯源Top5来源序列化器"""
    rank = serializers.IntegerField()
    part_name = serializers.CharField()
    qij = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True, required=False)
    wih = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True, required=False)
    concentration = serializers.DecimalField(max_digits=12, decimal_places=3, allow_null=True, required=False)


class SubstanceTraceabilityDetailSerializer(serializers.Serializer):
    """物质溯源详细信息序列化器"""
    substance_id = serializers.IntegerField()
    substance_name_cn = serializers.CharField()
    substance_name_en = serializers.CharField(allow_null=True, allow_blank=True)
    cas_no = serializers.CharField()
    retention_time = serializers.DecimalField(max_digits=8, decimal_places=2, allow_null=True)
    match_degree = serializers.DecimalField(max_digits=5, decimal_places=1, allow_null=True)
    concentration_ratio = serializers.DecimalField(max_digits=8, decimal_places=1, allow_null=True)
    concentration = serializers.DecimalField(max_digits=12, decimal_places=3, allow_null=True)
    odor_top5 = SubstanceTraceabilityTopSourceSerializer(many=True)
    organic_top5 = SubstanceTraceabilityTopSourceSerializer(many=True)
