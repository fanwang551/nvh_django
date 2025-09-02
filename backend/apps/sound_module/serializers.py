from rest_framework import serializers
from .models import SoundInsulationArea, SoundInsulationData, VehicleSoundInsulationData, VehicleReverberationData, SoundAbsorptionCoefficients
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


class VehicleSoundInsulationDataSerializer(serializers.ModelSerializer):
    """车型隔声量数据序列化器"""
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)
    vehicle_model_code = serializers.CharField(source='vehicle_model.cle_model_code', read_only=True)

    class Meta:
        model = VehicleSoundInsulationData
        fields = [
            'id', 'vehicle_model', 'vehicle_model_name', 'vehicle_model_code',
            'freq_200', 'freq_250', 'freq_315', 'freq_400', 'freq_500', 'freq_630',
            'freq_800', 'freq_1000', 'freq_1250', 'freq_1600', 'freq_2000', 'freq_2500',
            'freq_3150', 'freq_4000', 'freq_5000', 'freq_6300', 'freq_8000', 'freq_10000',
            'test_image_path', 'test_date', 'test_location', 'test_engineer', 'remarks',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VehicleSoundInsulationCompareSerializer(serializers.Serializer):
    """车型隔声量对比参数序列化器"""
    vehicle_model_ids = serializers.CharField(required=True, help_text='车型ID列表（逗号分隔）')

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


class VehicleReverberationDataSerializer(serializers.ModelSerializer):
    """车辆混响时间数据序列化器"""
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)
    vehicle_model_code = serializers.CharField(source='vehicle_model.cle_model_code', read_only=True)

    class Meta:
        model = VehicleReverberationData
        fields = [
            'id', 'vehicle_model', 'vehicle_model_name', 'vehicle_model_code',
            'freq_400', 'freq_500', 'freq_630', 'freq_800', 'freq_1000', 'freq_1250',
            'freq_1600', 'freq_2000', 'freq_2500', 'freq_3150', 'freq_4000', 'freq_5000',
            'freq_6300', 'freq_8000', 'freq_10000',
            'test_image_path', 'test_date', 'test_location', 'test_engineer', 'remarks',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VehicleReverberationCompareSerializer(serializers.Serializer):
    """车辆混响时间对比参数序列化器"""
    vehicle_model_ids = serializers.CharField(required=True, help_text='车型ID列表（逗号分隔）')

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


class SoundAbsorptionCoefficientsSerializer(serializers.ModelSerializer):
    """吸声系数数据序列化器"""
    
    class Meta:
        model = SoundAbsorptionCoefficients
        fields = [
            'id', 'part_name', 'material_composition', 'manufacturer',
            'test_institution', 'thickness', 'weight',
            # 测试值字段
            'test_value_125', 'test_value_160', 'test_value_200', 'test_value_250',
            'test_value_315', 'test_value_400', 'test_value_500', 'test_value_630',
            'test_value_800', 'test_value_1000', 'test_value_1250', 'test_value_1600',
            'test_value_2000', 'test_value_2500', 'test_value_3150', 'test_value_4000',
            'test_value_5000', 'test_value_6300', 'test_value_8000', 'test_value_10000',
            # 目标值字段
            'target_value_125', 'target_value_160', 'target_value_200', 'target_value_250',
            'target_value_315', 'target_value_400', 'target_value_500', 'target_value_630',
            'target_value_800', 'target_value_1000', 'target_value_1250', 'target_value_1600',
            'target_value_2000', 'target_value_2500', 'target_value_3150', 'target_value_4000',
            'target_value_5000', 'target_value_6300', 'target_value_8000', 'target_value_10000',
            # 测试相关信息
            'test_date', 'test_location', 'test_engineer', 'test_image_path', 'remarks',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SoundAbsorptionQuerySerializer(serializers.Serializer):
    """吸声系数查询参数序列化器"""
    part_name = serializers.CharField(required=False, help_text='零件名称')
    material_composition = serializers.CharField(required=False, help_text='材料组成')
    weight = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, help_text='克重(g/m²)')

    def validate(self, data):
        """验证查询参数"""
        if not any(data.values()):
            raise serializers.ValidationError("至少需要提供一个查询条件")
        return data


class PartNameOptionSerializer(serializers.Serializer):
    """零件名称选项序列化器"""
    value = serializers.CharField()
    label = serializers.CharField()


class MaterialCompositionOptionSerializer(serializers.Serializer):
    """材料组成选项序列化器"""
    value = serializers.CharField()
    label = serializers.CharField()
    part_name = serializers.CharField()


class WeightOptionSerializer(serializers.Serializer):
    """克重选项序列化器"""
    value = serializers.DecimalField(max_digits=8, decimal_places=2)
    label = serializers.CharField()
    part_name = serializers.CharField()
    material_composition = serializers.CharField()
