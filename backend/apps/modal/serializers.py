from rest_framework import serializers
from .models import VehicleModel, Component, TestProject, ModalData, AirtightnessTest, AirtightnessImage


class VehicleModelSerializer(serializers.ModelSerializer):
    """车型序列化器"""

    class Meta:
        model = VehicleModel
        fields = [
            'id', 'cle_model_code', 'vehicle_model_name', 'vin',
            'drive_type', 'configuration', 'production_year',
            'status'
        ]
        read_only_fields = ['id']


class ComponentSerializer(serializers.ModelSerializer):
    """零件序列化器"""

    class Meta:
        model = Component
        fields = [
            'id', 'component_name', 'category', 'component_brand',
            'component_model', 'component_code'
        ]
        read_only_fields = ['id']


class TestProjectSerializer(serializers.ModelSerializer):
    """测试项目序列化器"""
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)
    component_name = serializers.CharField(source='component.component_name', read_only=True)

    class Meta:
        model = TestProject
        fields = [
            'id', 'vehicle_model', 'vehicle_model_name',
            'component', 'component_name', 'test_type', 'test_date',
            'test_location', 'test_engineer', 'test_status',
            'excitation_method', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ModalDataSerializer(serializers.ModelSerializer):
    """模态数据序列化器"""
    test_project_id = serializers.IntegerField(source='test_project.id', read_only=True)
    vehicle_model_name = serializers.CharField(source='test_project.vehicle_model.vehicle_model_name', read_only=True)
    component_name = serializers.CharField(source='test_project.component.component_name', read_only=True)
    component_category = serializers.CharField(source='test_project.component.category', read_only=True)

    class Meta:
        model = ModalData
        fields = [
            'id', 'test_project', 'test_project_id', 'vehicle_model_name', 'component_name', 'component_category',
            'frequency', 'damping_ratio', 'mode_shape_description',
            'mode_shape_file', 'test_photo_file', 'notes',
            'created_at', 'updated_at', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ModalDataQuerySerializer(serializers.Serializer):
    """模态数据查询参数序列化器（支持多零件查询）"""
    vehicle_model_id = serializers.IntegerField(required=True, help_text='车型ID')
    component_ids = serializers.CharField(required=False, allow_blank=True, help_text='零件ID列表（逗号分隔，可选）')
    test_type = serializers.CharField(required=False, allow_blank=True, help_text='测试类型（可选）')

    def validate_vehicle_model_id(self, value):
        """验证车型ID是否存在"""
        if not VehicleModel.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的车型不存在")
        return value


class ModalDataCompareSerializer(serializers.Serializer):
    """模态数据对比参数序列化器"""
    component_id = serializers.IntegerField(required=True, help_text='零件ID')
    vehicle_model_ids = serializers.CharField(required=True, help_text='车型ID列表（逗号分隔）')
    test_statuses = serializers.CharField(required=False, allow_blank=True, help_text='测试状态列表（逗号分隔，可选）')
    mode_types = serializers.CharField(required=False, allow_blank=True, help_text='振型类型列表（逗号分隔，可选）')

    def validate_component_id(self, value):
        """验证零件ID是否存在"""
        if not Component.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的零件不存在")
        return value

    def validate_vehicle_model_ids(self, value):
        """验证车型ID列表"""
        if not value:
            raise serializers.ValidationError("车型ID列表不能为空")

        try:
            ids = [int(id.strip()) for id in value.split(',') if id.strip()]
            if not ids:
                raise serializers.ValidationError("车型ID列表不能为空")

            # 验证所有车型ID是否存在
            existing_count = VehicleModel.objects.filter(id__in=ids).count()
            if existing_count != len(ids):
                raise serializers.ValidationError("部分车型ID不存在")

            return ids
        except ValueError:
            raise serializers.ValidationError("车型ID格式错误")

    def validate_component_ids(self, value):
        """验证零件ID列表格式和存在性"""
        if not value:
            return value

        try:
            component_id_list = [int(id.strip()) for id in value.split(',') if id.strip()]
            if component_id_list:
                # 验证所有零件ID是否存在
                existing_ids = set(Component.objects.filter(id__in=component_id_list).values_list('id', flat=True))
                invalid_ids = set(component_id_list) - existing_ids
                if invalid_ids:
                    raise serializers.ValidationError(f"以下零件ID不存在: {', '.join(map(str, invalid_ids))}")
        except ValueError:
            raise serializers.ValidationError("零件ID格式错误，应为逗号分隔的数字")

        return value


class AirtightnessTestSerializer(serializers.ModelSerializer):
    """气密性测试序列化器"""
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)
    vehicle_model_code = serializers.CharField(source='vehicle_model.cle_model_code', read_only=True)

    class Meta:
        model = AirtightnessTest
        fields = [
            'id', 'vehicle_model', 'vehicle_model_name', 'vehicle_model_code',
            'test_date', 'test_engineer', 'test_location',
            'uncontrolled_leakage', 'left_pressure_valve', 'right_pressure_valve', 'ac_circulation_valve',
            'right_door_drain_hole', 'tailgate_drain_hole', 'right_door_outer_seal',
            'right_door_outer_opening', 'side_mirrors',
            'body_shell_leakage', 'other_area', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AirtightnessImageSerializer(serializers.ModelSerializer):
    """气密性测试图片序列化器"""
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)
    vehicle_model_code = serializers.CharField(source='vehicle_model.cle_model_code', read_only=True)

    class Meta:
        model = AirtightnessImage
        fields = [
            'id', 'vehicle_model', 'vehicle_model_name', 'vehicle_model_code',
            'front_compartment_image', 'door_image', 'tailgate_image',
            'upload_date', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AirtightnessCompareSerializer(serializers.Serializer):
    """气密性数据对比参数序列化器"""
    vehicle_model_ids = serializers.CharField(required=True, help_text='车型ID列表（逗号分隔）')

    def validate_vehicle_model_ids(self, value):
        """验证车型ID列表"""
        if not value:
            raise serializers.ValidationError("车型ID列表不能为空")

        try:
            ids = [int(id.strip()) for id in value.split(',') if id.strip()]
            if not ids:
                raise serializers.ValidationError("车型ID列表不能为空")

            # 验证所有车型ID是否存在
            existing_count = VehicleModel.objects.filter(id__in=ids).count()
            if existing_count != len(ids):
                raise serializers.ValidationError("部分车型ID不存在")

            return ids
        except ValueError:
            raise serializers.ValidationError("车型ID格式错误")
