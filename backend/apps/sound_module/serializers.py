from rest_framework import serializers
from .models import SoundInsulationArea, SoundInsulationData
from apps.modal.models import VehicleModel


class SoundInsulationAreaSerializer(serializers.ModelSerializer):
    """隔声区域序列化器"""

    class Meta:
        model = SoundInsulationArea
        fields = ['id', 'area_name', 'description']
        read_only_fields = ['id']


class SoundInsulationDataSerializer(serializers.ModelSerializer):
    """隔声量数据序列化器"""
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)
    area_name = serializers.CharField(source='area.area_name', read_only=True)

    class Meta:
        model = SoundInsulationData
        fields = [
            'id', 'vehicle_model', 'vehicle_model_name', 'area', 'area_name',
            'freq_200', 'freq_250', 'freq_315', 'freq_400', 'freq_500', 'freq_630',
            'freq_800', 'freq_1000', 'freq_1250', 'freq_1600', 'freq_2000', 'freq_2500',
            'freq_3150', 'freq_4000', 'freq_5000', 'freq_6300', 'freq_8000', 'freq_10000',
            'test_image_path', 'test_date', 'test_location', 'test_engineer', 'remarks',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SoundInsulationCompareSerializer(serializers.Serializer):
    """隔声量对比参数序列化器"""
    area_id = serializers.IntegerField(required=True, help_text='区域ID')
    vehicle_model_ids = serializers.CharField(required=True, help_text='车型ID列表（逗号分隔）')

    def validate_area_id(self, value):
        """验证区域ID是否存在"""
        if not SoundInsulationArea.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的区域不存在")
        return value

    def validate_vehicle_model_ids(self, value):
        """验证车型ID列表"""
        if not value.strip():
            raise serializers.ValidationError("车型ID列表不能为空")
        
        try:
            ids = [int(id.strip()) for id in value.split(',') if id.strip()]
            if not ids:
                raise serializers.ValidationError("车型ID列表不能为空")
            
            # 验证所有车型ID是否存在
            existing_ids = set(VehicleModel.objects.filter(id__in=ids).values_list('id', flat=True))
            invalid_ids = set(ids) - existing_ids
            if invalid_ids:
                raise serializers.ValidationError(f"以下车型ID不存在: {', '.join(map(str, invalid_ids))}")
                
        except ValueError:
            raise serializers.ValidationError("车型ID格式错误，请使用逗号分隔的数字")
        
        return value


class VehicleModelSimpleSerializer(serializers.ModelSerializer):
    """车型简单序列化器（用于级联查询）"""
    
    class Meta:
        model = VehicleModel
        fields = ['id', 'vehicle_model_name', 'cle_model_code']
        read_only_fields = ['id']
