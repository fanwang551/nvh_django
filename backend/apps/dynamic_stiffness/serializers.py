from rest_framework import serializers
from .models import DynamicStiffnessTest, DynamicStiffnessData
from apps.modal.models import VehicleModel


class DynamicStiffnessTestSerializer(serializers.ModelSerializer):
    """动刚度测试序列化器"""
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)
    
    class Meta:
        model = DynamicStiffnessTest
        fields = [
            'id', 'vehicle_model', 'vehicle_model_name', 'part_name',
            'test_date', 'test_location', 'test_engineer', 'analysis_engineer',
            'suspension_type', 'test_photo_path'
        ]
        read_only_fields = ['id']


class DynamicStiffnessDataSerializer(serializers.ModelSerializer):
    """动刚度数据序列化器"""
    vehicle_model_name = serializers.CharField(source='test.vehicle_model.vehicle_model_name', read_only=True)
    part_name = serializers.CharField(source='test.part_name', read_only=True)
    test_date = serializers.DateField(source='test.test_date', read_only=True)
    test_location = serializers.CharField(source='test.test_location', read_only=True)
    test_engineer = serializers.CharField(source='test.test_engineer', read_only=True)
    analysis_engineer = serializers.CharField(source='test.analysis_engineer', read_only=True)
    suspension_type = serializers.CharField(source='test.suspension_type', read_only=True)
    test_photo_path = serializers.CharField(source='test.test_photo_path', read_only=True)
    
    class Meta:
        model = DynamicStiffnessData
        fields = [
            'id', 'test', 'vehicle_model_name', 'part_name', 'test_date', 'test_location',
            'test_engineer', 'analysis_engineer', 'suspension_type', 'test_photo_path',
            'subsystem', 'test_point',
            # X方向数据
            'target_stiffness_x', 'freq_50_x', 'freq_80_x', 'freq_100_x', 'freq_125_x',
            'freq_160_x', 'freq_200_x', 'freq_250_x', 'freq_315_x', 'freq_350_x', 'freq_400_x',
            # Y方向数据
            'target_stiffness_y', 'freq_50_y', 'freq_80_y', 'freq_100_y', 'freq_125_y',
            'freq_160_y', 'freq_200_y', 'freq_250_y', 'freq_315_y', 'freq_350_y', 'freq_400_y',
            # Z方向数据
            'target_stiffness_z', 'freq_50_z', 'freq_80_z', 'freq_100_z', 'freq_125_z',
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
