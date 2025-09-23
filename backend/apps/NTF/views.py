from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from apps.NTF.models import NTFInfo
from apps.NTF.serializers import (
    NTFInfoDetailSerializer,
    NTFInfoListSerializer,
)
from utils.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def ntf_info_list(request):
    queryset = NTFInfo.objects.select_related('vehicle_model').all()

    vehicle_model = request.GET.get('vehicle_model')
    if vehicle_model:
        queryset = queryset.filter(vehicle_model_id=vehicle_model)

    queryset = queryset.order_by('-test_time')
    serializer = NTFInfoListSerializer(queryset, many=True)
    return Response.success(data=serializer.data, message='获取NTF测试信息成功')


@api_view(['GET'])
@permission_classes([AllowAny])
def ntf_info_detail(request, pk):
    try:
        instance = NTFInfo.objects.select_related('vehicle_model').prefetch_related('test_results').get(pk=pk)
    except NTFInfo.DoesNotExist:
        return Response.not_found(message='NTF测试信息不存在')

    serializer = NTFInfoDetailSerializer(instance)
    return Response.success(data=serializer.data, message='获取NTF测试详情成功')


@api_view(['GET'])
@permission_classes([AllowAny])
def ntf_info_by_vehicle(request, vehicle_id):
    instance = (
        NTFInfo.objects.select_related('vehicle_model')
        .prefetch_related('test_results')
        .filter(vehicle_model_id=vehicle_id)
        .order_by('-test_time')
        .first()
    )

    if not instance:
        return Response.not_found(message='未找到该车型的NTF测试信息')

    serializer = NTFInfoDetailSerializer(instance)
    return Response.success(data=serializer.data, message='获取车型NTF测试详情成功')

