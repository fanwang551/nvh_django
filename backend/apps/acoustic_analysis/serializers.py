from rest_framework import serializers

from apps.acoustic_analysis.models import AcousticTestData
from apps.modal.models import VehicleModel


class WorkConditionListSerializer(serializers.Serializer):
    vehicle_model_ids = serializers.CharField(required=True, help_text='车型ID列表，逗号分隔')

    def validate_vehicle_model_ids(self, value):
        try:
            ids = [int(x.strip()) for x in value.split(',') if x.strip()]
        except Exception:
            raise serializers.ValidationError('车型ID格式错误')

        if not ids:
            raise serializers.ValidationError('车型ID不能为空')

        exists = VehicleModel.objects.filter(id__in=ids).count()
        if exists != len(ids):
            raise serializers.ValidationError('部分车型ID不存在')
        return ids


class MeasurePointListSerializer(serializers.Serializer):
    vehicle_model_ids = serializers.CharField(required=True, help_text='车型ID列表，逗号分隔')
    work_conditions = serializers.CharField(required=True, help_text='工况列表，逗号分隔')

    def validate_vehicle_model_ids(self, value):
        try:
            ids = [int(x.strip()) for x in value.split(',') if x.strip()]
        except Exception:
            raise serializers.ValidationError('车型ID格式错误')
        if not ids:
            raise serializers.ValidationError('车型ID不能为空')
        exists = VehicleModel.objects.filter(id__in=ids).count()
        if exists != len(ids):
            raise serializers.ValidationError('部分车型ID不存在')
        return ids

    def validate_work_conditions(self, value):
        items = [x.strip() for x in value.split(',') if x.strip()]
        if not items:
            raise serializers.ValidationError('工况不能为空')
        return items


class AcousticQuerySerializer(serializers.Serializer):
    vehicle_model_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=False
    )
    work_conditions = serializers.ListField(
        child=serializers.CharField(max_length=100), allow_empty=False
    )
    measure_points = serializers.ListField(
        child=serializers.CharField(max_length=100), allow_empty=False
    )

    def validate(self, attrs):
        vm_ids = attrs.get('vehicle_model_ids')
        wc = attrs.get('work_conditions')
        mp = attrs.get('measure_points')

        # 校验车型ID存在
        cnt = VehicleModel.objects.filter(id__in=vm_ids).count()
        if cnt != len(vm_ids):
            raise serializers.ValidationError('部分车型ID不存在')

        # 限制最多10个组合
        combos = len(vm_ids) * len(wc) * len(mp)
        if combos > 10:
            raise serializers.ValidationError('每次查询的组合数量最多10条，请减少选择范围')
        return attrs


class AcousticTableItemSerializer(serializers.ModelSerializer):
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)
    work_condition = serializers.CharField(source='condition_point.work_condition', read_only=True)
    measure_point = serializers.CharField(source='condition_point.measure_point', read_only=True)
    measure_type = serializers.CharField(source='condition_point.measure_type', read_only=True)

    class Meta:
        model = AcousticTestData
        fields = (
            'id',
            'vehicle_model_name',
            'work_condition',
            'measure_point',
            'measure_type',
            'speech_clarity',
            'rms_value',
            'test_date',
        )


class SteadyStateQuerySerializer(serializers.Serializer):
    vehicle_model_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
    )
    work_conditions = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=False,
    )
    measure_points = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=False,
    )

    def validate(self, attrs):
        vm_ids = attrs.get('vehicle_model_ids') or []
        work_conditions = attrs.get('work_conditions') or []
        measure_points = attrs.get('measure_points') or []

        count = VehicleModel.objects.filter(id__in=vm_ids).count()
        if count != len(vm_ids):
            raise serializers.ValidationError('部分车型ID不存在')

        combinations = len(vm_ids) * len(work_conditions) * len(measure_points)
        if combinations > 200:
            raise serializers.ValidationError('每次查询的组合数量最多200条，请减少选择范围')
        return attrs
