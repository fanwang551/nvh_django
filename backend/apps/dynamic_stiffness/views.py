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

        # 子系统筛选（支持多选，逗号分隔）
        subsystem = request.GET.get('subsystem')
        if subsystem:
            # 支持传入逗号分隔的多个子系统名称
            parts = [s.strip() for s in subsystem.split(',') if s and s.strip()]
            if len(parts) > 1:
                queryset = queryset.filter(subsystem__in=parts)
            else:
                queryset = queryset.filter(subsystem=parts[0])

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
        vehicle_ids_param = request.GET.get('vehicle_ids')  # 支持多车型，逗号分隔

        # 构建查询条件
        queryset = MountIsolationData.objects.all()

        if vehicle_ids_param:
            try:
                id_list = [int(v) for v in vehicle_ids_param.split(',') if v.strip()]
                queryset = queryset.filter(test__vehicle_model_id__in=id_list)
            except ValueError:
                return Response.error(message="vehicle_ids 参数格式错误", status_code=status.HTTP_400_BAD_REQUEST)
        elif vehicle_model_id:
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


# ------------------- 悬置隔振率功能（重构版）API -------------------

@api_view(['GET'])
@permission_classes([])
def get_isolation_vehicle_models(request):
    """获取参与悬置隔振率测试的车型（去重），含能源类型。"""
    try:
        # 去重车型ID
        vehicle_ids = (
            VehicleMountIsolationTest.objects.values_list('vehicle_model_id', flat=True).distinct()
        )
        results = []
        for vid in vehicle_ids:
            try:
                vm = VehicleModel.objects.get(id=vid)
            except VehicleModel.DoesNotExist:
                continue
            # 优先读取测试表中的能源类型（若存在测试记录）
            latest_test = (
                VehicleMountIsolationTest.objects
                .filter(vehicle_model_id=vid)
                .order_by('-test_date')
                .first()
            )
            if latest_test is not None and latest_test.energy_type is not None:
                energy_type = int(latest_test.energy_type)
            else:
                # 回退：基于车型信息推断能源类型
                et = (vm.energy_type or '').strip()
                energy_type = 0 if ('油' in et or et == '燃油') else 1

            results.append({
                'id': vm.id,
                'name': vm.vehicle_model_name,
                'energy_type': energy_type,
            })

        return Response.success(data=results, message="获取车型列表成功")
    except Exception as e:
        return Response.error(message=f"获取车型列表失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])
def get_isolation_test_info(request):
    """获取选中车型的测试信息卡片数据（各车型最新一条）。"""
    try:
        vehicle_ids_param = request.GET.get('vehicle_ids')
        if not vehicle_ids_param:
            return Response.success(data=[], message="未提供车型ID")

        try:
            id_list = [int(v) for v in vehicle_ids_param.split(',') if v.strip()]
        except ValueError:
            return Response.error(message="vehicle_ids 参数格式错误", status_code=status.HTTP_400_BAD_REQUEST)

        data = []
        for vid in id_list:
            row = (
                VehicleMountIsolationTest.objects
                .filter(vehicle_model_id=vid)
                .values('vehicle_model_id', 'vehicle_model__vehicle_model_name', 'test_engineer', 'test_location', 'test_condition', 'test_date')
                .order_by('-test_date')
                .first()
            )
            if not row:
                # 无测试数据也返回基本车型名称
                try:
                    vm = VehicleModel.objects.get(id=vid)
                    data.append({
                        'vehicle_id': vm.id,
                        'vehicle_name': vm.vehicle_model_name,
                        'test_engineer': '',
                        'test_location': '',
                        'test_condition': '',
                        'test_date': None,
                    })
                except VehicleModel.DoesNotExist:
                    continue
                continue

            data.append({
                'vehicle_id': row['vehicle_model_id'],
                'vehicle_name': row['vehicle_model__vehicle_model_name'],
                'test_engineer': row.get('test_engineer') or '',
                'test_location': row.get('test_location') or '',
                'test_condition': row.get('test_condition') or '',
                'test_date': row.get('test_date'),
            })

        return Response.success(data=data, message="获取测试信息成功")
    except Exception as e:
        return Response.error(message=f"获取测试信息失败: {str(e)}")


@api_view(['POST'])
@permission_classes([])
def isolation_data_query(request):
    """悬置隔振率曲线数据查询（多车型/多测点/多方向）。"""
    try:
        payload = request.data or {}
        vehicle_ids = payload.get('vehicle_ids') or []
        measuring_points = payload.get('measuring_points') or []
        directions = payload.get('directions') or ['X', 'Y', 'Z']

        if not isinstance(vehicle_ids, list) or not vehicle_ids:
            return Response.error(message="vehicle_ids 不能为空", status_code=status.HTTP_400_BAD_REQUEST)

        # 统一能源类型：优先读取测试表energy_type；若无则回退到车型字段推断
        def map_energy_type_from_vehicle(vid):
            try:
                latest_test = (
                    VehicleMountIsolationTest.objects
                    .filter(vehicle_model_id=vid)
                    .order_by('-test_date')
                    .first()
                )
                if latest_test is not None and latest_test.energy_type is not None:
                    return int(latest_test.energy_type)
                vm = VehicleModel.objects.get(id=vid)
                et = (vm.energy_type or '').strip()
                return 0 if ('油' in et or et == '燃油') else 1
            except VehicleModel.DoesNotExist:
                raise

        energy_types = []
        for vid in vehicle_ids:
            try:
                energy_types.append(map_energy_type_from_vehicle(vid))
            except VehicleModel.DoesNotExist:
                return Response.error(message=f"车型不存在: {vid}", status_code=status.HTTP_400_BAD_REQUEST)

        if len(set(energy_types)) > 1:
            return Response.error(message="只能选择相同能源类型的车型（燃油车或纯电/混动车）", status_code=status.HTTP_400_BAD_REQUEST)

        energy_type = energy_types[0]
        x_axis_label = "速度 (km/h)" if energy_type == 0 else "转速 (rpm)"

        # 查询数据：选中车型 + 可选测点筛选
        base_queryset = (
            MountIsolationData.objects
            .filter(test__vehicle_model_id__in=vehicle_ids)
        )
        if measuring_points:
            base_queryset = base_queryset.filter(measuring_point__in=measuring_points)

        # 选择必要字段（包含曲线JSON）
        queryset = (
            base_queryset
            .values(
                'test__vehicle_model_id',
                'test__vehicle_model__vehicle_model_name',
                'measuring_point',
                'test__test_date',
                'speed_or_rpm',
                'x_active', 'x_passive', 'x_isolation',
                'y_active', 'y_passive', 'y_isolation',
                'z_active', 'z_passive', 'z_isolation',
            )
            .order_by('measuring_point', '-test__test_date')
        )

        # 聚合为 vehicle_id + measuring_point 的最近一条
        seen = set()
        results = []
        dir_map = {'X': 'x', 'Y': 'y', 'Z': 'z'}
        for row in queryset:
            key = (row['test__vehicle_model_id'], row['measuring_point'])
            if key in seen:
                continue
            seen.add(key)

            data_entry = {
                'vehicle_id': row['test__vehicle_model_id'],
                'vehicle_name': row['test__vehicle_model__vehicle_model_name'],
                'measuring_point': row['measuring_point'],
                'speed_or_rpm': row.get('speed_or_rpm') or [],
            }

            # 仅返回所需方向（数组字段在未迁移前返回空数组占位）
            for d in directions:
                key_prefix = dir_map.get(d.upper())
                if not key_prefix:
                    continue
                if key_prefix == 'x':
                    data_entry[key_prefix] = {
                        'active': row.get('x_active') or [],
                        'passive': row.get('x_passive') or [],
                        'isolation': row.get('x_isolation') or [],
                    }
                elif key_prefix == 'y':
                    data_entry[key_prefix] = {
                        'active': row.get('y_active') or [],
                        'passive': row.get('y_passive') or [],
                        'isolation': row.get('y_isolation') or [],
                    }
                elif key_prefix == 'z':
                    data_entry[key_prefix] = {
                        'active': row.get('z_active') or [],
                        'passive': row.get('z_passive') or [],
                        'isolation': row.get('z_isolation') or [],
                    }

            results.append(data_entry)

        return Response.success(data={
            'energy_type': energy_type,
            'x_axis_label': x_axis_label,
            'data': results,
        }, message="查询成功")
    except Exception as e:
        return Response.error(message=f"查询失败: {str(e)}")


## 旧版悬置隔振率列表查询接口已移除（改用 POST /isolation-data/query/）


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
