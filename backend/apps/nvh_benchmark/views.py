from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from apps.modal.models import VehicleModel
from utils.response import Response

from .serializers import NVHBenchmarkQuerySerializer, VehicleOptionSerializer
from .services import build_benchmark_payload


@api_view(['GET'])
@permission_classes([AllowAny])
def list_vehicle_models(request):
    queryset =VehicleModel.objects.filter(status='active')
    serializer = VehicleOptionSerializer(queryset, many=True)
    return Response.success(data=serializer.data, message='获取车型列表成功')


@api_view(['POST'])
@permission_classes([AllowAny])
def get_benchmark_overview(request):
    serializer = NVHBenchmarkQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response.bad_request(message='查询参数错误', data=serializer.errors)

    data = serializer.validated_data
    payload = build_benchmark_payload(
        main_vehicle_id=data['main_vehicle_id'],
        vehicle_ids=data['vehicle_ids'],
        include_chassis=data['include_chassis'],
        include_acoustic=data['include_acoustic_package'],
    )
    return Response.success(data=payload, message='获取NVH对标数据成功')
