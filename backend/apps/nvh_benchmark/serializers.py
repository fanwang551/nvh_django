from collections import OrderedDict

from rest_framework import serializers

from apps.modal.models import VehicleModel


class VehicleOptionSerializer(serializers.ModelSerializer):
    """车型下拉列表序列化器，附带默认对标车型"""

    default_benchmark_ids = serializers.SerializerMethodField()

    class Meta:
        model = VehicleModel
        fields = [
            'id',
            'vehicle_model_name',
            'cle_model_code',
            'drive_type',
            'energy_type',
            'suspension_type',
            'subframe_type',
            'default_benchmark_ids',
        ]

    def get_default_benchmark_ids(self, obj):
        if getattr(obj, 'benchmark_vehicle_id', None):
            return [obj.benchmark_vehicle_id]
        return []


class NVHBenchmarkQuerySerializer(serializers.Serializer):
    main_vehicle_id = serializers.IntegerField(min_value=1)
    benchmark_vehicle_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
        default=list,
    )
    include_chassis = serializers.BooleanField(required=False, default=True)
    include_acoustic_package = serializers.BooleanField(required=False, default=True)

    def validate(self, attrs):
        main_vehicle_id = attrs.get('main_vehicle_id')
        benchmark_vehicle_ids = attrs.get('benchmark_vehicle_ids') or []

        ordered_ids = [main_vehicle_id] + benchmark_vehicle_ids
        # 去重但保留顺序，确保主车型始终在首位
        deduped_ids = list(OrderedDict.fromkeys([vid for vid in ordered_ids if vid]))

        existing_ids = set(
            VehicleModel.objects.filter(id__in=deduped_ids).values_list('id', flat=True)
        )
        missing = [vid for vid in deduped_ids if vid not in existing_ids]
        if missing:
            raise serializers.ValidationError(f"以下车型ID不存在: {', '.join(map(str, missing))}")

        attrs['vehicle_ids'] = deduped_ids
        attrs['benchmark_vehicle_ids'] = [
            vid for vid in benchmark_vehicle_ids if vid != main_vehicle_id
        ]
        return attrs
