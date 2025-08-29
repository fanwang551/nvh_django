from rest_framework import serializers
from .models import VehicleModel, Component, TestProject, ModalData


class VehicleModelSerializer(serializers.ModelSerializer):
    """车型序列化器"""
    
    class Meta:
        model = VehicleModel
        fields = [
            'id', 'cle_model_code', 'vehicle_model_name', 'vin', 
            'drive_type', 'configuration', 'production_year', 
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ComponentSerializer(serializers.ModelSerializer):
    """零件序列化器"""
    
    class Meta:
        model = Component
        fields = [
            'id', 'component_name', 'category', 'component_brand', 
            'component_model', 'component_code', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestProjectSerializer(serializers.ModelSerializer):
    """测试项目序列化器"""
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)
    component_name = serializers.CharField(source='component.component_name', read_only=True)
    
    class Meta:
        model = TestProject
        fields = [
            'id', 'project_code', 'vehicle_model', 'vehicle_model_name',
            'component', 'component_name', 'test_type', 'test_date',
            'test_location', 'test_engineer', 'test_status', 
            'excitation_method', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ModalDataSerializer(serializers.ModelSerializer):
    """模态数据序列化器"""
    test_project_code = serializers.CharField(source='test_project.project_code', read_only=True)
    vehicle_model_name = serializers.CharField(source='test_project.vehicle_model.vehicle_model_name', read_only=True)
    component_name = serializers.CharField(source='test_project.component.component_name', read_only=True)
    
    class Meta:
        model = ModalData
        fields = [
            'id', 'test_project', 'test_project_code', 'vehicle_model_name', 'component_name',
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
