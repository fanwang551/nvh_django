from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from utils.response import Response
from utils.pagination import PageNumberPaginationUtil
from .models import VehicleModel, Component, TestProject, ModalData
from .serializers import (
    VehicleModelSerializer, ComponentSerializer,
    ModalDataSerializer, ModalDataQuerySerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vehicle_model_list(request):
    """获取车型列表（无分页）"""
    try:
        queryset = VehicleModel.objects.filter(status='active')

        # 支持按车型名称搜索
        search = request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(vehicle_model_name__icontains=search) |
                Q(cle_model_code__icontains=search)
            )

        # 按创建时间排序
        queryset = queryset.order_by('-created_at')

        serializer = VehicleModelSerializer(queryset, many=True)
        return Response.success(data=serializer.data, message="获取车型列表成功")

    except Exception as e:
        return Response.error(message=f"获取车型列表失败: {str(e)}")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def component_list(request):
    """获取零件列表（支持按车型筛选，无分页）"""
    try:
        vehicle_model_id = request.GET.get('vehicle_model_id')

        if vehicle_model_id:
            # 根据车型ID获取相关的零件（通过测试项目关联）
            component_ids = TestProject.objects.filter(
                vehicle_model_id=vehicle_model_id
            ).values_list('component_id', flat=True).distinct()

            queryset = Component.objects.filter(id__in=component_ids)
        else:
            # 获取所有零件
            queryset = Component.objects.all()

        # 支持按零件名称搜索
        search = request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(component_name__icontains=search) |
                Q(component_code__icontains=search) |
                Q(category__icontains=search)
            )

        # 按分类和名称排序
        queryset = queryset.order_by('category', 'component_name')

        serializer = ComponentSerializer(queryset, many=True)
        return Response.success(data=serializer.data, message="获取零件列表成功")

    except Exception as e:
        return Response.error(message=f"获取零件列表失败: {str(e)}")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def modal_data_query(request):
    """模态数据查询（支持多零件筛选）"""
    try:
        # 获取查询参数
        vehicle_model_id = request.GET.get('vehicle_model_id')
        if not vehicle_model_id:
            return Response.error(message="车型ID不能为空", status_code=status.HTTP_400_BAD_REQUEST)

        # 验证车型是否存在
        if not VehicleModel.objects.filter(id=vehicle_model_id).exists():
            return Response.error(message="指定的车型不存在", status_code=status.HTTP_400_BAD_REQUEST)

        # 构建查询条件
        queryset = ModalData.objects.select_related(
            'test_project',
            'test_project__vehicle_model',
            'test_project__component'
        ).filter(test_project__vehicle_model_id=vehicle_model_id)

        # 支持多零件ID筛选
        component_ids = request.GET.get('component_ids')
        if component_ids:
            try:
                # 支持逗号分隔的多个零件ID
                component_id_list = [int(id.strip()) for id in component_ids.split(',') if id.strip()]
                if component_id_list:
                    queryset = queryset.filter(test_project__component_id__in=component_id_list)
            except ValueError:
                return Response.error(message="零件ID格式错误", status_code=status.HTTP_400_BAD_REQUEST)

        # 支持按测试类型搜索
        test_type = request.GET.get('test_type')
        if test_type:
            queryset = queryset.filter(test_project__test_type__icontains=test_type)

        # 排序：按频率升序
        queryset = queryset.order_by('frequency', '-created_at')

        # 分页处理
        paginator = PageNumberPaginationUtil()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = ModalDataSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ModalDataSerializer(queryset, many=True)
        return Response.success(data=serializer.data, message="查询模态数据成功")

    except Exception as e:
        return Response.error(message=f"查询模态数据失败: {str(e)}")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def modal_data_statistics(request):
    """模态数据统计信息"""
    try:
        vehicle_model_id = request.GET.get('vehicle_model_id')
        component_id = request.GET.get('component_id')

        if not vehicle_model_id:
            return Response.error(message="车型ID不能为空")

        # 基础查询
        queryset = ModalData.objects.filter(test_project__vehicle_model_id=vehicle_model_id)
        if component_id:
            queryset = queryset.filter(test_project__component_id=component_id)

        # 统计信息
        total_count = queryset.count()
        if total_count > 0:
            frequencies = queryset.values_list('frequency', flat=True)
            min_freq = min(frequencies)
            max_freq = max(frequencies)
            avg_freq = sum(frequencies) / len(frequencies)
        else:
            min_freq = max_freq = avg_freq = 0

        statistics = {
            'total_count': total_count,
            'frequency_range': {
                'min': float(min_freq) if min_freq else 0,
                'max': float(max_freq) if max_freq else 0,
                'avg': round(avg_freq, 2) if avg_freq else 0
            }
        }

        return Response.success(data=statistics, message="获取统计信息成功")

    except Exception as e:
        return Response.error(message=f"获取统计信息失败: {str(e)}")
