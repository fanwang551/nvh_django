from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from utils.response import Response
from .models import (
    DynamicStiffnessTest, DynamicStiffnessData, 
    VehicleMountIsolationTest, MountIsolationData,
    VehicleSuspensionIsolationTest, SuspensionIsolationData
)
from apps.modal.models import VehicleModel
from .serializers import (
    DynamicStiffnessTestSerializer,
    DynamicStiffnessDataSerializer,
    DynamicStiffnessQuerySerializer,
    VehicleMountIsolationTestSerializer,
    MountIsolationDataSerializer,
    MountIsolationQuerySerializer,
    VehicleSuspensionIsolationTestSerializer,
    SuspensionIsolationDataSerializer,
    SuspensionIsolationQuerySerializer
)


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_part_names(request):
    """获取零件名称列表（基于车型筛选）"""
    try:
        vehicle_model_id = request.GET.get('vehicle_model_id')
        
        # 构建查询条件
        queryset = DynamicStiffnessTest.objects.all()
        
        if vehicle_model_id:
            try:
                vehicle_model_id = int(vehicle_model_id)
                queryset = queryset.filter(vehicle_model_id=vehicle_model_id)
            except ValueError:
                return Response.error(message="车型ID格式错误", status_code=status.HTTP_400_BAD_REQUEST)
        
        # 获取不重复的零件名称
        part_names = queryset.values_list('part_name', flat=True).distinct().order_by('part_name')
        
        # 转换为选项格式
        options = [{'value': name, 'label': name} for name in part_names]
        
        return Response.success(data=options, message="获取零件名称列表成功")
        
    except Exception as e:
        return Response.error(message=f"获取零件名称列表失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_subsystems(request):
    """获取子系统列表（基于车型和零件筛选）"""
    try:
        vehicle_model_id = request.GET.get('vehicle_model_id')
        part_name = request.GET.get('part_name')
        
        # 构建查询条件
        queryset = DynamicStiffnessData.objects.select_related('test')
        
        if vehicle_model_id:
            try:
                vehicle_model_id = int(vehicle_model_id)
                queryset = queryset.filter(test__vehicle_model_id=vehicle_model_id)
            except ValueError:
                return Response.error(message="车型ID格式错误", status_code=status.HTTP_400_BAD_REQUEST)
        
        if part_name:
            queryset = queryset.filter(test__part_name=part_name)
        
        # 获取不重复的子系统
        subsystems = queryset.values_list('subsystem', flat=True).distinct().order_by('subsystem')
        
        # 转换为选项格式
        options = [{'value': name, 'label': name} for name in subsystems]
        
        return Response.success(data=options, message="获取子系统列表成功")
        
    except Exception as e:
        return Response.error(message=f"获取子系统列表失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_test_points(request):
    """获取测点列表（基于车型、零件和子系统筛选）"""
    try:
        vehicle_model_id = request.GET.get('vehicle_model_id')
        part_name = request.GET.get('part_name')
        subsystem = request.GET.get('subsystem')
        
        # 构建查询条件
        queryset = DynamicStiffnessData.objects.select_related('test')
        
        if vehicle_model_id:
            try:
                vehicle_model_id = int(vehicle_model_id)
                queryset = queryset.filter(test__vehicle_model_id=vehicle_model_id)
            except ValueError:
                return Response.error(message="车型ID格式错误", status_code=status.HTTP_400_BAD_REQUEST)
        
        if part_name:
            queryset = queryset.filter(test__part_name=part_name)
            
        if subsystem:
            queryset = queryset.filter(subsystem=subsystem)
        
        # 获取不重复的测点
        test_points = queryset.values_list('test_point', flat=True).distinct().order_by('test_point')
        
        # 转换为选项格式
        options = [{'value': name, 'label': name} for name in test_points]
        
        return Response.success(data=options, message="获取测点列表成功")
        
    except Exception as e:
        return Response.error(message=f"获取测点列表失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def dynamic_stiffness_query(request):
    """动刚度数据查询（无分页）"""
    try:
        # 获取查询参数
        vehicle_model_id = request.GET.get('vehicle_model_id')
        if not vehicle_model_id:
            return Response.error(message="车型ID不能为空", status_code=status.HTTP_400_BAD_REQUEST)

        # 验证车型是否存在
        if not VehicleModel.objects.filter(id=vehicle_model_id).exists():
            return Response.error(message="指定的车型不存在", status_code=status.HTTP_400_BAD_REQUEST)

        # 构建查询条件
        queryset = DynamicStiffnessData.objects.select_related(
            'test',
            'test__vehicle_model'
        ).filter(test__vehicle_model_id=vehicle_model_id)

        # 零件名称筛选
        part_name = request.GET.get('part_name')
        if part_name:
            queryset = queryset.filter(test__part_name=part_name)

        # 子系统筛选
        subsystem = request.GET.get('subsystem')
        if subsystem:
            queryset = queryset.filter(subsystem=subsystem)

        # 测点筛选（支持多选）
        test_points = request.GET.get('test_points')
        if test_points:
            test_point_list = [point.strip() for point in test_points.split(',') if point.strip()]
            if test_point_list:
                queryset = queryset.filter(test_point__in=test_point_list)

        # 排序：按子系统、测点排序
        queryset = queryset.order_by('subsystem', 'test_point')

        # 序列化数据（无分页）
        serializer = DynamicStiffnessDataSerializer(queryset, many=True)
        
        return Response.success(data={
            'count': queryset.count(),
            'results': serializer.data
        }, message="查询动刚度数据成功")

    except Exception as e:
        return Response.error(message=f"查询动刚度数据失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_measuring_points(request):
    """获取测点列表（基于车型筛选）"""
    try:
        vehicle_model_id = request.GET.get('vehicle_model_id')

        # 构建查询条件
        queryset = MountIsolationData.objects.all()

        if vehicle_model_id:
            try:
                vehicle_model_id = int(vehicle_model_id)
                queryset = queryset.filter(test__vehicle_model_id=vehicle_model_id)
            except ValueError:
                return Response.error(message="车型ID格式错误", status_code=status.HTTP_400_BAD_REQUEST)

        # 获取不重复的测点名称
        measuring_points = queryset.values_list('measuring_point', flat=True).distinct().order_by('measuring_point')

        # 转换为选项格式
        options = [{'value': point, 'label': point} for point in measuring_points]

        return Response.success(data=options, message="获取测点列表成功")

    except Exception as e:
        return Response.error(message=f"获取测点列表失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def mount_isolation_query(request):
    """悬置隔振率数据查询（无分页）"""
    try:
        # 获取查询参数
        vehicle_model_id = request.GET.get('vehicle_model_id')
        if not vehicle_model_id:
            return Response.error(message="车型ID不能为空", status_code=status.HTTP_400_BAD_REQUEST)

        # 验证车型是否存在
        if not VehicleModel.objects.filter(id=vehicle_model_id).exists():
            return Response.error(message="指定的车型不存在", status_code=status.HTTP_400_BAD_REQUEST)

        # 构建查询条件
        queryset = MountIsolationData.objects.select_related(
            'test',
            'test__vehicle_model'
        ).filter(test__vehicle_model_id=vehicle_model_id)

        # 测点筛选
        measuring_points = request.GET.get('measuring_points')
        if measuring_points:
            point_list = [point.strip() for point in measuring_points.split(',') if point.strip()]
            if point_list:
                queryset = queryset.filter(measuring_point__in=point_list)

        # 排序：按测点排序
        queryset = queryset.order_by('measuring_point')

        # 序列化数据（无分页）
        serializer = MountIsolationDataSerializer(queryset, many=True)

        return Response.success(data={
            'count': queryset.count(),
            'results': serializer.data
        }, message="查询悬置隔振率数据成功")

    except Exception as e:
        return Response.error(message=f"查询悬置隔振率数据失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_suspension_measuring_points(request):
    """获取悬架隔振率测点列表（基于车型筛选）"""
    try:
        vehicle_model_id = request.GET.get('vehicle_model_id')

        # 构建查询条件
        queryset = SuspensionIsolationData.objects.all()

        if vehicle_model_id:
            try:
                vehicle_model_id = int(vehicle_model_id)
                queryset = queryset.filter(test__vehicle_model_id=vehicle_model_id)
            except ValueError:
                return Response.error(message="车型ID格式错误", status_code=status.HTTP_400_BAD_REQUEST)

        # 获取不重复的测点名称
        measuring_points = queryset.values_list('measuring_point', flat=True).distinct().order_by('measuring_point')

        # 转换为选项格式
        options = [{'value': point, 'label': point} for point in measuring_points]

        return Response.success(data=options, message="获取测点列表成功")

    except Exception as e:
        return Response.error(message=f"获取测点列表失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def suspension_isolation_query(request):
    """悬架隔振率数据查询（无分页）"""
    try:
        # 获取查询参数
        vehicle_model_id = request.GET.get('vehicle_model_id')
        if not vehicle_model_id:
            return Response.error(message="车型ID不能为空", status_code=status.HTTP_400_BAD_REQUEST)

        # 验证车型是否存在
        if not VehicleModel.objects.filter(id=vehicle_model_id).exists():
            return Response.error(message="指定的车型不存在", status_code=status.HTTP_400_BAD_REQUEST)

        # 构建查询条件
        queryset = SuspensionIsolationData.objects.select_related(
            'test',
            'test__vehicle_model'
        ).filter(test__vehicle_model_id=vehicle_model_id)

        # 测点筛选
        measuring_points = request.GET.get('measuring_points')
        if measuring_points:
            point_list = [point.strip() for point in measuring_points.split(',') if point.strip()]
            if point_list:
                queryset = queryset.filter(measuring_point__in=point_list)

        # 排序：按测点排序
        queryset = queryset.order_by('measuring_point')

        # 序列化数据（无分页）
        serializer = SuspensionIsolationDataSerializer(queryset, many=True)

        return Response.success(data={
            'count': queryset.count(),
            'results': serializer.data
        }, message="查询悬架隔振率数据成功")

    except Exception as e:
        return Response.error(message=f"查询悬架隔振率数据失败: {str(e)}")
