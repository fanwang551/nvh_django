from rest_framework import serializers
from .models import SampleInfo, VocResult
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


class VocResultSerializer(serializers.ModelSerializer):
    """VOC检测结果序列化器"""
    sample_info = SampleInfoSerializer(source='sample', read_only=True)
    
    # 格式化显示保留3位小数
    benzene_formatted = serializers.SerializerMethodField()
    toluene_formatted = serializers.SerializerMethodField()
    ethylbenzene_formatted = serializers.SerializerMethodField()
    xylene_formatted = serializers.SerializerMethodField()
    styrene_formatted = serializers.SerializerMethodField()
    formaldehyde_formatted = serializers.SerializerMethodField()
    acetaldehyde_formatted = serializers.SerializerMethodField()
    acrolein_formatted = serializers.SerializerMethodField()
    tvoc_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = VocResult
        fields = [
            'id', 'sample', 'sample_info', 'benzene', 'toluene', 'ethylbenzene', 
            'xylene', 'styrene', 'formaldehyde', 'acetaldehyde', 'acrolein', 'tvoc', 
            'test_date', 'benzene_formatted', 'toluene_formatted', 'ethylbenzene_formatted',
            'xylene_formatted', 'styrene_formatted', 'formaldehyde_formatted', 
            'acetaldehyde_formatted', 'acrolein_formatted', 'tvoc_formatted'
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
