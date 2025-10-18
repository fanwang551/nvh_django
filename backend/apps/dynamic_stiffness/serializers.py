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
    part_name = serializers.CharField(source='test.part_name', read_only=True)
    test_date = serializers.DateField(source='test.test_date', read_only=True)
    test_location = serializers.CharField(source='test.test_location', read_only=True)
    test_engineer = serializers.CharField(source='test.test_engineer', read_only=True)
    analysis_engineer = serializers.CharField(source='test.analysis_engineer', read_only=True)
    test_photo_path = serializers.JSONField(source='test.test_photo_path', read_only=True, allow_null=True)
    
    class Meta:
        model = DynamicStiffnessData
        fields = [
            'id', 'test', 'vehicle_model_name', 'part_name', 'test_date', 'test_location',
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


class VehicleMountIsolationTestSerializer(serializers.ModelSerializer):
    """整车悬置隔振率测试序列化器"""
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)

    class Meta:
        model = VehicleMountIsolationTest
        fields = [
            'id', 'vehicle_model', 'vehicle_model_name', 'test_date', 'test_location',
            'test_engineer', 'suspension_type', 'tire_pressure',
            # 座椅导轨振动 AC OFF/ON
            'seat_vib_x_ac_off', 'seat_vib_y_ac_off', 'seat_vib_z_ac_off',
            'seat_vib_x_ac_on', 'seat_vib_y_ac_on', 'seat_vib_z_ac_on',
            # 方向盘振动 AC OFF/ON
            'steering_vib_x_ac_off', 'steering_vib_y_ac_off', 'steering_vib_z_ac_off',
            'steering_vib_x_ac_on', 'steering_vib_y_ac_on', 'steering_vib_z_ac_on',
            # 内噪声 AC OFF/ON
            'cabin_noise_front_ac_off', 'cabin_noise_rear_ac_off',
            'cabin_noise_front_ac_on', 'cabin_noise_rear_ac_on'
        ]
        read_only_fields = ['id']


class MountIsolationDataSerializer(serializers.ModelSerializer):
    """悬置隔振率试验数据序列化器"""
    vehicle_model_name = serializers.CharField(source='test.vehicle_model.vehicle_model_name', read_only=True)
    test_date = serializers.DateField(source='test.test_date', read_only=True)
    test_location = serializers.CharField(source='test.test_location', read_only=True)
    test_engineer = serializers.CharField(source='test.test_engineer', read_only=True)
    suspension_type = serializers.CharField(source='test.suspension_type', read_only=True)
    tire_pressure = serializers.CharField(source='test.tire_pressure', read_only=True)

    # 基本信息字段 - 座椅导轨振动 AC OFF/ON
    seat_vib_x_ac_off = serializers.FloatField(source='test.seat_vib_x_ac_off', read_only=True)
    seat_vib_y_ac_off = serializers.FloatField(source='test.seat_vib_y_ac_off', read_only=True)
    seat_vib_z_ac_off = serializers.FloatField(source='test.seat_vib_z_ac_off', read_only=True)
    seat_vib_x_ac_on = serializers.FloatField(source='test.seat_vib_x_ac_on', read_only=True)
    seat_vib_y_ac_on = serializers.FloatField(source='test.seat_vib_y_ac_on', read_only=True)
    seat_vib_z_ac_on = serializers.FloatField(source='test.seat_vib_z_ac_on', read_only=True)

    # 基本信息字段 - 方向盘振动 AC OFF/ON
    steering_vib_x_ac_off = serializers.FloatField(source='test.steering_vib_x_ac_off', read_only=True)
    steering_vib_y_ac_off = serializers.FloatField(source='test.steering_vib_y_ac_off', read_only=True)
    steering_vib_z_ac_off = serializers.FloatField(source='test.steering_vib_z_ac_off', read_only=True)
    steering_vib_x_ac_on = serializers.FloatField(source='test.steering_vib_x_ac_on', read_only=True)
    steering_vib_y_ac_on = serializers.FloatField(source='test.steering_vib_y_ac_on', read_only=True)
    steering_vib_z_ac_on = serializers.FloatField(source='test.steering_vib_z_ac_on', read_only=True)

    # 基本信息字段 - 内噪声 AC OFF/ON
    cabin_noise_front_ac_off = serializers.FloatField(source='test.cabin_noise_front_ac_off', read_only=True)
    cabin_noise_rear_ac_off = serializers.FloatField(source='test.cabin_noise_rear_ac_off', read_only=True)
    cabin_noise_front_ac_on = serializers.FloatField(source='test.cabin_noise_front_ac_on', read_only=True)
    cabin_noise_rear_ac_on = serializers.FloatField(source='test.cabin_noise_rear_ac_on', read_only=True)

    class Meta:
        model = MountIsolationData
        fields = [
            'id', 'test', 'vehicle_model_name', 'test_date', 'test_location',
            'test_engineer', 'suspension_type', 'tire_pressure',
            # 座椅导轨振动 AC OFF/ON
            'seat_vib_x_ac_off', 'seat_vib_y_ac_off', 'seat_vib_z_ac_off',
            'seat_vib_x_ac_on', 'seat_vib_y_ac_on', 'seat_vib_z_ac_on',
            # 方向盘振动 AC OFF/ON
            'steering_vib_x_ac_off', 'steering_vib_y_ac_off', 'steering_vib_z_ac_off',
            'steering_vib_x_ac_on', 'steering_vib_y_ac_on', 'steering_vib_z_ac_on',
            # 内噪声 AC OFF/ON
            'cabin_noise_front_ac_off', 'cabin_noise_rear_ac_off',
            'cabin_noise_front_ac_on', 'cabin_noise_rear_ac_on',
            'measuring_point',
            # X方向数据
            'x_ac_off_isolation', 'x_ac_off_vibration', 'x_ac_on_isolation', 'x_ac_on_vibration',
            # Y方向数据
            'y_ac_off_isolation', 'y_ac_off_vibration', 'y_ac_on_isolation', 'y_ac_on_vibration',
            # Z方向数据
            'z_ac_off_isolation', 'z_ac_off_vibration', 'z_ac_on_isolation', 'z_ac_on_vibration',
            # 图片路径
            'layout_image_path', 'curve_image_path'
        ]
        read_only_fields = ['id']


class MountIsolationQuerySerializer(serializers.Serializer):
    """悬置隔振率查询参数序列化器"""
    vehicle_model_id = serializers.IntegerField(required=True, help_text='车型ID')
    measuring_points = serializers.CharField(required=False, allow_blank=True, help_text='测点列表（逗号分隔，可选）')

    def validate_vehicle_model_id(self, value):
        """验证车型ID是否存在"""
        if not VehicleModel.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的车型不存在")
        return value


class VehicleSuspensionIsolationTestSerializer(serializers.ModelSerializer):
    """整车悬架隔振率测试序列化器"""
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)

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
    suspension_type = serializers.CharField(source='test.suspension_type', read_only=True)
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
