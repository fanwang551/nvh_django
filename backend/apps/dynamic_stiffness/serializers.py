from rest_framework import serializers
from .models import (
    DynamicStiffnessTest, DynamicStiffnessData, 
    VehicleMountIsolationTest, MountIsolationData,
    VehicleSuspensionIsolationTest, SuspensionIsolationData
)
from apps.modal.models import VehicleModel


class DynamicStiffnessTestSerializer(serializers.ModelSerializer):
    """动刚度测试序列化器"""
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)
    
    class Meta:
        model = DynamicStiffnessTest
        fields = [
            'id', 'vehicle_model', 'vehicle_model_name', 'part_name',
            'test_date', 'test_location', 'test_engineer', 'analysis_engineer',
            'test_photo_path'
        ]
        read_only_fields = ['id']


class DynamicStiffnessDataSerializer(serializers.ModelSerializer):
    """动刚度数据序列化器"""
    vehicle_model_name = serializers.CharField(source='test.vehicle_model.vehicle_model_name', read_only=True)
    suspension_type = serializers.CharField(source='test.vehicle_model.suspension_type', read_only=True, allow_null=True)
    part_name = serializers.CharField(source='test.part_name', read_only=True)
    test_date = serializers.DateField(source='test.test_date', read_only=True)
    test_location = serializers.CharField(source='test.test_location', read_only=True)
    test_engineer = serializers.CharField(source='test.test_engineer', read_only=True)
    analysis_engineer = serializers.CharField(source='test.analysis_engineer', read_only=True)
    test_photo_path = serializers.JSONField(source='test.test_photo_path', read_only=True, allow_null=True)
    
    class Meta:
        model = DynamicStiffnessData
        fields = [
            'id', 'test', 'vehicle_model_name', 'suspension_type', 'part_name', 'test_date', 'test_location',
            'test_engineer', 'analysis_engineer', 'test_photo_path',
            'subsystem', 'test_point',
            # X方向数据
            'target_stiffness_x', 'freq_50_x', 'freq_63_x', 'freq_80_x', 'freq_100_x', 'freq_125_x',
            'freq_160_x', 'freq_200_x', 'freq_250_x', 'freq_315_x', 'freq_350_x', 'freq_400_x',
            # Y方向数据
            'target_stiffness_y', 'freq_50_y', 'freq_63_y', 'freq_80_y', 'freq_100_y', 'freq_125_y',
            'freq_160_y', 'freq_200_y', 'freq_250_y', 'freq_315_y', 'freq_350_y', 'freq_400_y',
            # Z方向数据
            'target_stiffness_z', 'freq_50_z', 'freq_63_z', 'freq_80_z', 'freq_100_z', 'freq_125_z',
            'freq_160_z', 'freq_200_z', 'freq_250_z', 'freq_315_z', 'freq_350_z', 'freq_400_z',
            # 图片路径
            'layout_image', 'curve_image'
        ]
        read_only_fields = ['id']


class DynamicStiffnessQuerySerializer(serializers.Serializer):
    """动刚度查询参数序列化器"""
    vehicle_model_id = serializers.IntegerField(required=True, help_text='车型ID')
    part_name = serializers.CharField(required=False, allow_blank=True, help_text='零件名称（可选）')
    subsystem = serializers.CharField(required=False, allow_blank=True, help_text='子系统（可选）')
    test_points = serializers.CharField(required=False, allow_blank=True, help_text='测点列表（逗号分隔，可选）')

    def validate_vehicle_model_id(self, value):
        """验证车型ID是否存在"""
        if not VehicleModel.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的车型不存在")
        return value


## 旧版悬置隔振率序列化器（含 AC ON/OFF 单值）已移除


class VehicleSuspensionIsolationTestSerializer(serializers.ModelSerializer):
    """整车悬架隔振率测试序列化器"""
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)
    # 模型字段已移除，改从车型信息读取悬挂形式
    suspension_type = serializers.CharField(source='vehicle_model.suspension_type', read_only=True, allow_null=True)

    class Meta:
        model = VehicleSuspensionIsolationTest
        fields = [
            'id', 'vehicle_model', 'vehicle_model_name', 'test_date', 'test_location',
            'test_engineer', 'suspension_type', 'tire_pressure', 'test_condition'
        ]
        read_only_fields = ['id']


class SuspensionIsolationDataSerializer(serializers.ModelSerializer):
    """悬架隔振率试验数据序列化器"""
    vehicle_model_name = serializers.CharField(source='test.vehicle_model.vehicle_model_name', read_only=True)
    test_date = serializers.DateField(source='test.test_date', read_only=True)
    test_location = serializers.CharField(source='test.test_location', read_only=True)
    test_engineer = serializers.CharField(source='test.test_engineer', read_only=True)
    # 模型字段已移除，改从车型信息读取悬挂形式
    suspension_type = serializers.CharField(source='test.vehicle_model.suspension_type', read_only=True, allow_null=True)
    tire_pressure = serializers.CharField(source='test.tire_pressure', read_only=True)
    test_condition = serializers.CharField(source='test.test_condition', read_only=True)

    class Meta:
        model = SuspensionIsolationData
        fields = [
            'id', 'test', 'vehicle_model_name', 'test_date', 'test_location',
            'test_engineer', 'suspension_type', 'tire_pressure', 'test_condition',
            'measuring_point',
            # X方向数据
            'x_active_value', 'x_passive_value', 'x_isolation_rate',
            # Y方向数据
            'y_active_value', 'y_passive_value', 'y_isolation_rate',
            # Z方向数据
            'z_active_value', 'z_passive_value', 'z_isolation_rate',
            # 图片路径
            'layout_image_path', 'curve_image_path'
        ]
        read_only_fields = ['id']


class SuspensionIsolationQuerySerializer(serializers.Serializer):
    """悬架隔振率查询参数序列化器"""
    vehicle_model_id = serializers.IntegerField(required=True, help_text='车型ID')
    measuring_points = serializers.CharField(required=False, allow_blank=True, help_text='测点列表（逗号分隔，可选）')

    def validate_vehicle_model_id(self, value):
        """验证车型ID是否存在"""
        if not VehicleModel.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的车型不存在")
        return value


# ------------------- 悬置隔振率功能（重构版）附加序列化器 -------------------

class VehicleModelOptionSerializer(serializers.Serializer):
    """车型选项（去重后，用于多选框）"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    energy_type = serializers.IntegerField()  # 0=燃油 1=纯电/混动


class TestInfoSerializer(serializers.Serializer):
    """测试信息卡片数据"""
    vehicle_id = serializers.IntegerField()
    vehicle_name = serializers.CharField()
    test_engineer = serializers.CharField(allow_blank=True, required=False)
    test_location = serializers.CharField(allow_blank=True, required=False)
    test_condition = serializers.CharField(allow_blank=True, required=False)
    test_date = serializers.DateTimeField(allow_null=True, required=False)
