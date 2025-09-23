from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from utils.response import Response
from apps.wheel_performance.models import WheelPerformance
from apps.wheel_performance.serializers import (
    WheelPerformanceSerializer,
    WheelPerformanceCreateUpdateSerializer,
)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def wheel_performance_list(request):
    """查询或创建车轮性能数据。"""
    if request.method == 'GET':
        queryset = WheelPerformance.objects.select_related('vehicle_model').all()

        raw_vehicle_model_ids = request.GET.getlist('vehicle_model_ids')
        vehicle_model_ids = []

        for value in raw_vehicle_model_ids:
            if not value:
                continue
            for part in value.split(','):
                part = part.strip()
                if not part:
                    continue
                try:
                    vehicle_model_ids.append(int(part))
                except (TypeError, ValueError):
                    continue

        if vehicle_model_ids:
            queryset = queryset.filter(vehicle_model_id__in=vehicle_model_ids)
        else:
            vehicle_model = request.GET.get('vehicle_model')
            if vehicle_model:
                queryset = queryset.filter(vehicle_model_id=vehicle_model)

        queryset = queryset.order_by('vehicle_model__vehicle_model_name', 'tire_brand', 'tire_model')
        serializer = WheelPerformanceSerializer(queryset, many=True)
        return Response.success(data=serializer.data, message='获取车轮性能数据成功')

    serializer = WheelPerformanceCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        output = WheelPerformanceSerializer(instance).data
        return Response.success(data=output, message='创建车轮性能数据成功', status_code=status.HTTP_201_CREATED)

    return Response.error(message='创建车轮性能数据失败', data=serializer.errors)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def wheel_performance_detail(request, pk):
    """获取、更新或删除指定车轮性能数据。"""
    try:
        instance = WheelPerformance.objects.select_related('vehicle_model').get(pk=pk)
    except WheelPerformance.DoesNotExist:
        return Response.not_found(message='车轮性能数据不存在')

    if request.method == 'GET':
        serializer = WheelPerformanceSerializer(instance)
        return Response.success(data=serializer.data, message='获取车轮性能数据成功')

    if request.method == 'PUT':
        serializer = WheelPerformanceCreateUpdateSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            output = WheelPerformanceSerializer(instance).data
            return Response.success(data=output, message='更新车轮性能数据成功')
        return Response.error(message='更新车轮性能数据失败', data=serializer.errors)

    instance.delete()
    return Response.success(message='删除车轮性能数据成功')
