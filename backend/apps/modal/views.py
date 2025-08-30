from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from utils.response import Response
from utils.pagination import PageNumberPaginationUtil
from .models import VehicleModel, Component, TestProject, ModalData, AirtightnessTest, AirtightnessImage
from .serializers import (
    VehicleModelSerializer, ComponentSerializer,
    ModalDataSerializer, ModalDataQuerySerializer, ModalDataCompareSerializer,
    AirtightnessTestSerializer, AirtightnessCompareSerializer, AirtightnessImageSerializer
)


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
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

        # 按ID排序
        queryset = queryset.order_by('id')

        serializer = VehicleModelSerializer(queryset, many=True)
        return Response.success(data=serializer.data, message="获取车型列表成功")

    except Exception as e:
        return Response.error(message=f"获取车型列表失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
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


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_related_vehicle_models(request):
    """根据零件ID获取相关的车型列表"""
    try:
        component_id = request.GET.get('component_id')
        if not component_id:
            return Response.error(message="零件ID不能为空", status_code=status.HTTP_400_BAD_REQUEST)

        # 验证零件是否存在
        if not Component.objects.filter(id=component_id).exists():
            return Response.error(message="指定的零件不存在", status_code=status.HTTP_400_BAD_REQUEST)

        # 获取该零件相关的所有车型
        vehicle_models = VehicleModel.objects.filter(
            testproject__component_id=component_id,
            status='active'
        ).distinct().order_by('id')

        serializer = VehicleModelSerializer(vehicle_models, many=True)
        return Response.success(data=serializer.data)

    except Exception as e:
        return Response.error(message=f"获取相关车型失败: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_test_statuses(request):
    """获取测试状态选项"""
    try:
        component_id = request.GET.get('component_id')
        vehicle_model_ids = request.GET.get('vehicle_model_ids')

        if not component_id:
            return Response.error(message="零件ID不能为空", status_code=status.HTTP_400_BAD_REQUEST)

        # 构建查询条件
        queryset = TestProject.objects.filter(component_id=component_id)

        if vehicle_model_ids:
            try:
                ids = [int(id.strip()) for id in vehicle_model_ids.split(',') if id.strip()]
                queryset = queryset.filter(vehicle_model_id__in=ids)
            except ValueError:
                return Response.error(message="车型ID格式错误", status_code=status.HTTP_400_BAD_REQUEST)

        # 获取不重复的测试状态
        test_statuses = queryset.values_list('test_status', flat=True).distinct()
        test_statuses = [status for status in test_statuses if status]  # 过滤空值

        return Response.success(data=test_statuses)

    except Exception as e:
        return Response.error(message=f"获取测试状态失败: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_mode_types(request):
    """获取振型类型选项"""
    try:
        component_id = request.GET.get('component_id')
        vehicle_model_ids = request.GET.get('vehicle_model_ids')
        test_statuses = request.GET.get('test_statuses')

        if not component_id:
            return Response.error(message="零件ID不能为空", status_code=status.HTTP_400_BAD_REQUEST)

        # 构建查询条件
        queryset = ModalData.objects.select_related('test_project').filter(
            test_project__component_id=component_id
        )

        if vehicle_model_ids:
            try:
                ids = [int(id.strip()) for id in vehicle_model_ids.split(',') if id.strip()]
                queryset = queryset.filter(test_project__vehicle_model_id__in=ids)
            except ValueError:
                return Response.error(message="车型ID格式错误", status_code=status.HTTP_400_BAD_REQUEST)

        if test_statuses:
            status_list = [status.strip() for status in test_statuses.split(',') if status.strip()]
            queryset = queryset.filter(test_project__test_status__in=status_list)

        # 获取不重复的振型类型（从mode_shape_description字段）
        mode_types = queryset.values_list('mode_shape_description', flat=True).distinct()
        mode_types = [mode_type for mode_type in mode_types if mode_type]  # 过滤空值

        return Response.success(data=mode_types)

    except Exception as e:
        return Response.error(message=f"获取振型类型失败: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])  # 临时允许匿名访问用于测试
def modal_data_compare(request):
    """模态数据对比"""
    try:
        serializer = ModalDataCompareSerializer(data=request.data)
        if not serializer.is_valid():
            return Response.error(message="参数验证失败", data=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        component_id = validated_data['component_id']
        vehicle_model_ids = validated_data['vehicle_model_ids']
        test_statuses = validated_data.get('test_statuses', '').split(',') if validated_data.get('test_statuses') else []
        mode_types = validated_data.get('mode_types', '').split(',') if validated_data.get('mode_types') else []

        # 清理空值
        test_statuses = [status.strip() for status in test_statuses if status.strip()]
        mode_types = [mode_type.strip() for mode_type in mode_types if mode_type.strip()]

        # 构建查询条件
        queryset = ModalData.objects.select_related(
            'test_project',
            'test_project__vehicle_model',
            'test_project__component'
        ).filter(
            test_project__component_id=component_id,
            test_project__vehicle_model_id__in=vehicle_model_ids
        )

        if test_statuses:
            queryset = queryset.filter(test_project__test_status__in=test_statuses)

        if mode_types:
            queryset = queryset.filter(mode_shape_description__in=mode_types)

        # 获取对比数据
        compare_data = []
        for modal_data in queryset:
            vehicle_name = modal_data.test_project.vehicle_model.vehicle_model_name
            test_status = modal_data.test_project.test_status or '未知状态'

            # 根据业务规则决定显示格式
            if len(vehicle_model_ids) == 1 and len(test_statuses) > 1:
                # 单车型多测试状态：显示为"车型名_测试状态"
                display_name = f"{vehicle_name}_{test_status}"
            else:
                # 多车型或单测试状态：只显示车型名
                display_name = vehicle_name

            compare_data.append({
                'id': modal_data.id,
                'vehicle_model_id': modal_data.test_project.vehicle_model.id,
                'vehicle_model_name': vehicle_name,
                'test_status': test_status,
                'display_name': display_name,
                'mode_type': modal_data.mode_shape_description,
                'mode_shape_description': modal_data.mode_shape_description,
                'frequency': float(modal_data.frequency),
                'damping_ratio': float(modal_data.damping_ratio) if modal_data.damping_ratio else None,
                'mode_shape_file': modal_data.mode_shape_file,
                'test_photo_file': modal_data.test_photo_file,
                'notes': modal_data.notes,
                'component_name': modal_data.test_project.component.component_name
            })

        return Response.success(data=compare_data, message="对比数据获取成功")

    except Exception as e:
        return Response.error(message=f"获取对比数据失败: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])  # 临时允许匿名访问用于测试
def airtightness_data_compare(request):
    """气密性数据对比"""
    try:
        serializer = AirtightnessCompareSerializer(data=request.data)
        if not serializer.is_valid():
            return Response.error(message="参数验证失败", data=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        vehicle_model_ids = validated_data['vehicle_model_ids']

        # 查询气密性测试数据
        queryset = AirtightnessTest.objects.select_related('vehicle_model').filter(
            vehicle_model_id__in=vehicle_model_ids
        ).order_by('vehicle_model__id', '-test_date')

        # 为每个车型获取最新的测试数据
        vehicle_data = {}
        for test in queryset:
            vehicle_id = test.vehicle_model.id
            if vehicle_id not in vehicle_data:
                vehicle_data[vehicle_id] = test

        # 构建对比数据结构
        compare_data = {
            'vehicle_models': [],
            'leakage_data': []
        }

        # 获取车型信息
        for vehicle_id in vehicle_model_ids:
            if vehicle_id in vehicle_data:
                test = vehicle_data[vehicle_id]
                compare_data['vehicle_models'].append({
                    'id': test.vehicle_model.id,
                    'name': test.vehicle_model.vehicle_model_name,
                    'code': test.vehicle_model.cle_model_code,
                    'test_date': test.test_date.strftime('%Y-%m-%d') if test.test_date else None
                })

        # 定义泄漏量数据结构
        leakage_categories = [
            {
                'category': '整车不可控泄漏量',
                'items': [
                    {'name': '整车不可控泄漏量', 'field': 'uncontrolled_leakage'}
                ]
            },
            {
                'category': '阀系统',
                'items': [
                    {'name': '左侧泄压阀', 'field': 'left_pressure_valve'},
                    {'name': '右侧泄压阀', 'field': 'right_pressure_valve'},
                    {'name': '空调内外循环阀', 'field': 'ac_circulation_valve'}
                ]
            },
            {
                'category': '门系统',
                'items': [
                    {'name': '右侧门漏液孔', 'field': 'right_door_drain_hole'},
                    {'name': '尾门漏液孔', 'field': 'tailgate_drain_hole'},
                    {'name': '右侧门外水切', 'field': 'right_door_outer_seal'},
                    {'name': '右侧门外开', 'field': 'right_door_outer_opening'},
                    {'name': '两侧外后视镜', 'field': 'side_mirrors'}
                ]
            },
            {
                'category': '白车身',
                'items': [
                    {'name': '白车身泄漏量', 'field': 'body_shell_leakage'}
                ]
            },
            {
                'category': '其他区域',
                'items': [
                    {'name': '其他区域', 'field': 'other_area'}
                ]
            }
        ]

        # 构建泄漏量对比数据
        for category in leakage_categories:
            category_data = {
                'category': category['category'],
                'items': []
            }

            for item in category['items']:
                item_data = {
                    'name': item['name'],
                    'values': []
                }

                # 为每个车型获取对应的泄漏量数值
                for vehicle_id in vehicle_model_ids:
                    if vehicle_id in vehicle_data:
                        test = vehicle_data[vehicle_id]
                        value = getattr(test, item['field'], None)
                        # 格式化数值：保留1位小数，空值显示为"-"
                        if value is not None:
                            item_data['values'].append(f"{float(value):.1f}")
                        else:
                            item_data['values'].append("-")
                    else:
                        item_data['values'].append("-")

                category_data['items'].append(item_data)

            compare_data['leakage_data'].append(category_data)

        return Response.success(data=compare_data, message="气密性对比数据获取成功")

    except Exception as e:
        return Response.error(message=f"获取气密性对比数据失败: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def airtightness_images_query(request):
    """气密性测试图片查询"""
    try:
        # 获取查询参数
        vehicle_model_ids = request.GET.get('vehicle_model_ids', '')

        # 构建查询条件
        queryset = AirtightnessImage.objects.select_related('vehicle_model')

        # 如果指定了车型ID，进行筛选
        if vehicle_model_ids:
            try:
                ids = [int(id.strip()) for id in vehicle_model_ids.split(',') if id.strip()]
                if ids:
                    queryset = queryset.filter(vehicle_model_id__in=ids)
            except ValueError:
                return Response.error(message="车型ID格式错误", status_code=status.HTTP_400_BAD_REQUEST)

        # 只查询激活状态的车型
        queryset = queryset.filter(vehicle_model__status='active')

        # 按车型ID和创建时间排序
        queryset = queryset.order_by('vehicle_model__id', '-created_at')

        # 序列化数据
        serializer = AirtightnessImageSerializer(queryset, many=True)

        return Response.success(data=serializer.data, message="获取气密性图片数据成功")

    except Exception as e:
        return Response.error(message=f"获取气密性图片数据失败: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
