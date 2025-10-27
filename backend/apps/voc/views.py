from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.core.paginator import Paginator
from utils.response import Response
from .models import SampleInfo, VocOdorResult, SubstancesTest, SubstancesTestDetail, Substance
from .serializers import (
    VocOdorResultSerializer, VocQuerySerializer, VocChartDataSerializer,
    PartNameOptionSerializer, VehicleModelOptionSerializer, StatusOptionSerializer,
    SubstancesTestSerializer, SubstancesTestDetailSerializer, SubstanceSerializer,
    SubstancesQuerySerializer
)
from apps.modal.models import VehicleModel


@api_view(['GET'])
@permission_classes([])
def voc_data_list(request):
    """获取VOC数据列表"""
    try:
        # 使用查询序列化器验证参数
        query_serializer = VocQuerySerializer(data=request.GET)
        query_serializer.is_valid(raise_exception=True)
        
        # 获取查询参数
        vehicle_model_id = query_serializer.validated_data.get('vehicle_model_id')
        part_name = query_serializer.validated_data.get('part_name', '')
        status_value = query_serializer.validated_data.get('status', '')
        test_order_no = query_serializer.validated_data.get('test_order_no', '')
        page = query_serializer.validated_data.get('page', 1)
        page_size = query_serializer.validated_data.get('page_size', 10)
        
        # 构建查询条件
        queryset = VocOdorResult.objects.select_related('sample', 'sample__vehicle_model').all()
        
        if vehicle_model_id:
            queryset = queryset.filter(sample__vehicle_model_id=vehicle_model_id)
        if part_name:
            queryset = queryset.filter(sample__part_name__icontains=part_name)
        if status_value:
            queryset = queryset.filter(sample__status=status_value)
        if test_order_no:
            queryset = queryset.filter(sample__test_order_no__icontains=test_order_no)
        
        # 分页处理
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # 序列化数据
        serializer = VocOdorResultSerializer(page_obj, many=True)
        
        return Response.success(data={
            'results': serializer.data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'page_size': page_size
            }
        }, message="获取VOC数据成功")
        
    except Exception as e:
        return Response.error(message=f"获取VOC数据失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])
def part_name_options(request):
    """获取零件名称选项列表"""
    try:
        part_names = SampleInfo.objects.values_list('part_name', flat=True).distinct()
        options = [{'value': name, 'label': name} for name in part_names if name]
        serializer = PartNameOptionSerializer(options, many=True)
        return Response.success(data=serializer.data, message="获取零件名称选项成功")
        
    except Exception as e:
        return Response.error(message=f"获取零件名称选项失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])
def vehicle_model_options(request):
    """获取车型选项列表"""
    try:
        # 只返回有VOC数据的车型
        vehicle_models = VehicleModel.objects.filter(
            id__in=SampleInfo.objects.values_list('vehicle_model_id', flat=True).distinct()
        ).values('id', 'vehicle_model_name').order_by('vehicle_model_name')
        
        options = [{'value': item['id'], 'label': item['vehicle_model_name']} for item in vehicle_models]
        serializer = VehicleModelOptionSerializer(options, many=True)
        return Response.success(data=serializer.data, message="获取车型选项成功")
        
    except Exception as e:
        return Response.error(message=f"获取车型选项失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])
def status_options(request):
    """获取状态选项列表"""
    try:
        # 从数据库中获取所有实际使用的状态值
        status_values = SampleInfo.objects.values_list('status', flat=True).distinct()
        # 过滤掉空值并创建选项列表
        options = [{'value': status, 'label': status} for status in status_values if status]
        serializer = StatusOptionSerializer(options, many=True)
        return Response.success(data=serializer.data, message="获取状态选项成功")
        
    except Exception as e:
        return Response.error(message=f"获取状态选项失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])
def development_stage_options(request):
    """获取开发阶段选项列表"""
    try:
        # 从数据库中获取所有实际使用的开发阶段值
        stage_values = SampleInfo.objects.values_list('development_stage', flat=True).distinct()
        # 过滤掉空值并创建选项列表
        options = [{'value': stage, 'label': stage} for stage in stage_values if stage]
        serializer = StatusOptionSerializer(options, many=True)
        return Response.success(data=serializer.data, message="获取开发阶段选项成功")
        
    except Exception as e:
        return Response.error(message=f"获取开发阶段选项失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])
def voc_chart_data(request):
    """获取VOC图表数据"""
    try:
        # 获取参数
        main_group = request.GET.get('main_group', 'part_name')  # 主分组：part_name 或 status
        sub_group = request.GET.get('sub_group', 'status')  # 副分组：status 或 part_name
        selected_compounds = request.GET.getlist('compounds')  # 选择的VOC物质
        
        # 默认选择的VOC物质（如果未指定）
        if not selected_compounds:
            selected_compounds = ['benzene', 'toluene', 'ethylbenzene', 'formaldehyde', 'tvoc']
        
        # 构建查询条件
        queryset = VocOdorResult.objects.select_related('sample', 'sample__vehicle_model').all()
        
        # 根据主分组和副分组进行分组统计
        from django.db.models import Avg, Count
        
        # 构建分组字段
        if main_group == 'part_name':
            main_field = 'sample__part_name'
        elif main_group == 'status':
            main_field = 'sample__status'
        else:
            main_field = 'sample__part_name'  # 默认
            
        if sub_group == 'part_name':
            sub_field = 'sample__part_name'
        elif sub_group == 'status':
            sub_field = 'sample__status'
        else:
            sub_field = 'sample__status'  # 默认
        
        # 构建聚合查询
        aggregates = {}
        for compound in selected_compounds:
            if compound in ['benzene', 'toluene', 'ethylbenzene', 'xylene', 'styrene', 
                           'formaldehyde', 'acetaldehyde', 'acrolein', 'tvoc']:
                aggregates[compound] = Avg(compound)
        
        # 分组统计数据
        chart_data = queryset.values(main_field, sub_field).annotate(**aggregates).order_by(main_field, sub_field)
        
        # 格式化图表数据
        formatted_data = []
        for item in chart_data:
            data_point = {
                'main_group': item[main_field] or '未知',
                'sub_group': item[sub_field] or '未知',
            }
            # 添加选择的VOC物质数据
            for compound in selected_compounds:
                data_point[compound] = item[compound]
            formatted_data.append(data_point)
        
        serializer = VocChartDataSerializer(formatted_data, many=True)
        return Response.success(data=serializer.data, message="获取VOC图表数据成功")
        
    except Exception as e:
        return Response.error(message=f"获取VOC图表数据失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])
def voc_statistics(request):
    """获取VOC统计数据"""
    try:
        # 总体统计
        total_samples = SampleInfo.objects.count()
        # 获取实际存在的状态值进行统计
        status_stats = SampleInfo.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 构建状态统计字典
        status_counts = {item['status']: item['count'] for item in status_stats}
        completed_samples = status_counts.get('completed', 0)
        pending_samples = status_counts.get('pending', 0)
        testing_samples = status_counts.get('testing', 0)
        
        # 各零件数量统计
        part_stats = SampleInfo.objects.values('part_name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # VOC物质平均值统计
        from django.db.models import Avg
        avg_values = VocOdorResult.objects.aggregate(
            avg_benzene=Avg('benzene'),
            avg_toluene=Avg('toluene'),
            avg_ethylbenzene=Avg('ethylbenzene'),
            avg_xylene=Avg('xylene'),
            avg_styrene=Avg('styrene'),
            avg_formaldehyde=Avg('formaldehyde'),
            avg_acetaldehyde=Avg('acetaldehyde'),
            avg_acrolein=Avg('acrolein'),
            avg_tvoc=Avg('tvoc')
        )
        
        return Response.success(data={
            'overview': {
                'total_samples': total_samples,
                'completed_samples': completed_samples,
                'pending_samples': pending_samples,
                'testing_samples': testing_samples,
            },
            'part_statistics': list(part_stats),
            'status_statistics': list(status_stats),
            'average_values': avg_values
        }, message="获取VOC统计数据成功")
        
    except Exception as e:
        return Response.error(message=f"获取VOC统计数据失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])
def voc_row_chart_data(request):
    """获取单行VOC数据的图表数据"""
    try:
        # 获取参数
        result_id = request.GET.get('result_id')
        
        if not result_id:
            return Response.error(message="缺少result_id参数")
        
        # 获取当前行数据
        try:
            current_result = VocOdorResult.objects.select_related(
                'sample', 'sample__vehicle_model'
            ).get(id=result_id)
        except VocOdorResult.DoesNotExist:
            return Response.error(message="数据不存在")
        
        current_sample = current_result.sample
        project_name = current_sample.vehicle_model.vehicle_model_name
        part_name = current_sample.part_name
        
        # 判断场景：整车 vs 非整车
        is_whole_vehicle = part_name == "整车"
        
        # 构建查询条件
        if is_whole_vehicle:
            # 场景A：整车 - 筛选项目名相同且零件名为"整车"的数据
            queryset = VocOdorResult.objects.select_related(
                'sample', 'sample__vehicle_model'
            ).filter(
                sample__vehicle_model__vehicle_model_name=project_name,
                sample__part_name="整车"
            )
        else:
            # 场景B：零部件 - 筛选项目名和零件名都相同的数据
            queryset = VocOdorResult.objects.select_related(
                'sample', 'sample__vehicle_model'
            ).filter(
                sample__vehicle_model__vehicle_model_name=project_name,
                sample__part_name=part_name
            )
        
        # X轴：固定8种物质
        x_axis = ["苯", "甲苯", "二甲苯", "乙苯", "苯乙烯", "甲醛", "乙醛", "TVOC"]
        compound_fields = ["benzene", "toluene", "xylene", "ethylbenzene", 
                          "styrene", "formaldehyde", "acetaldehyde", "tvoc"]
        
        # 构建系列数据
        series = []
        series_data = {}
        
        for result in queryset:
            sample = result.sample
            
            # 构建系列名称
            if is_whole_vehicle:
                # 场景A：检测状态-开发阶段
                series_name = f"{sample.status or '未知'}-{sample.development_stage or '未知'}"
            else:
                # 场景B：零部件名-开发阶段
                series_name = f"{sample.part_name or '未知'}-{sample.development_stage or '未知'}"
            
            # 提取VOC数据
            voc_values = []
            for field in compound_fields:
                value = getattr(result, field)
                # 转换为浮点数，None转为0
                voc_values.append(float(value) if value is not None else 0)
            
            # 添加到系列数据（使用系列名称作为key）
            if series_name not in series_data:
                series_data[series_name] = {
                    'name': series_name,
                    'data': voc_values,
                    'type': 'bar'
                }
        
        # 转换为列表
        series = list(series_data.values())
        
        return Response.success(data={
            'xAxis': x_axis,
            'series': series,
            'scenario': 'whole_vehicle' if is_whole_vehicle else 'part',
            'project_name': project_name,
            'part_name': part_name
        }, message="获取图表数据成功")
        
    except Exception as e:
        return Response.error(message=f"获取图表数据失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])
def odor_row_chart_data(request):
    """获取单行气味数据的图表数据"""
    try:
        # 获取参数
        result_id = request.GET.get('result_id')
        
        if not result_id:
            return Response.error(message="缺少result_id参数")
        
        # 获取当前行数据
        try:
            current_result = VocOdorResult.objects.select_related(
                'sample', 'sample__vehicle_model'
            ).get(id=result_id)
        except VocOdorResult.DoesNotExist:
            return Response.error(message="数据不存在")
        
        current_sample = current_result.sample
        project_name = current_sample.vehicle_model.vehicle_model_name
        part_name = current_sample.part_name
        
        # 判断场景：整车 vs 非整车
        is_whole_vehicle = part_name == "整车"
        
        # 构建查询条件
        if is_whole_vehicle:
            # 场景A：整车 - 筛选项目名相同且零件名为"整车"的数据
            queryset = VocOdorResult.objects.select_related(
                'sample', 'sample__vehicle_model'
            ).filter(
                sample__vehicle_model__vehicle_model_name=project_name,
                sample__part_name="整车"
            )
        else:
            # 场景B：零部件 - 筛选项目名和零件名都相同的数据
            queryset = VocOdorResult.objects.select_related(
                'sample', 'sample__vehicle_model'
            ).filter(
                sample__vehicle_model__vehicle_model_name=project_name,
                sample__part_name=part_name
            )
        
        # X轴根据场景不同
        if is_whole_vehicle:
            x_axis = ["动态-前排", "动态-后排", "静态-前排", "静态-后排", "气味均值"]
            odor_fields = ["dynamic_front", "dynamic_rear", "static_front", "static_rear", "odor_mean"]
        else:
            x_axis = ["气味均值"]
            odor_fields = ["odor_mean"]
        
        # 构建系列数据
        series_data = {}
        
        for result in queryset:
            sample = result.sample
            
            # 构建系列名称
            if is_whole_vehicle:
                # 场景A：项目名-开发阶段
                series_name = f"{project_name}-{sample.development_stage or '未知'}"
            else:
                # 场景B：零部件名-开发阶段
                series_name = f"{part_name}-{sample.development_stage or '未知'}"
            
            # 提取气味数据
            odor_values = []
            for field in odor_fields:
                value = getattr(result, field)
                # 转换为浮点数，None转为0
                odor_values.append(float(value) if value is not None else 0)
            
            # 添加到系列数据（使用系列名称作为key）
            if series_name not in series_data:
                series_data[series_name] = {
                    'name': series_name,
                    'data': odor_values,
                    'type': 'bar'
                }
        
        # 转换为列表
        series = list(series_data.values())
        
        return Response.success(data={
            'xAxis': x_axis,
            'series': series,
            'scenario': 'whole_vehicle' if is_whole_vehicle else 'part',
            'project_name': project_name,
            'part_name': part_name
        }, message="获取气味图表数据成功")
        
    except Exception as e:
        return Response.error(message=f"获取气味图表数据失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])
def substances_test_list(request):
    """获取全谱检测测试信息列表"""
    try:
        query_serializer = SubstancesQuerySerializer(data=request.GET)
        query_serializer.is_valid(raise_exception=True)
        
        vehicle_model_id = query_serializer.validated_data.get('vehicle_model_id')
        part_name = query_serializer.validated_data.get('part_name', '')
        status_value = query_serializer.validated_data.get('status', '')
        development_stage = query_serializer.validated_data.get('development_stage', '')
        test_order_no = query_serializer.validated_data.get('test_order_no', '')
        sample_no = query_serializer.validated_data.get('sample_no', '')
        test_date_start = query_serializer.validated_data.get('test_date_start')
        test_date_end = query_serializer.validated_data.get('test_date_end')
        page = query_serializer.validated_data.get('page', 1)
        page_size = query_serializer.validated_data.get('page_size', 10)
        
        queryset = SubstancesTest.objects.select_related('sample', 'sample__vehicle_model').all()
        
        if vehicle_model_id:
            queryset = queryset.filter(sample__vehicle_model_id=vehicle_model_id)
        if part_name:
            queryset = queryset.filter(sample__part_name__icontains=part_name)
        if status_value:
            queryset = queryset.filter(sample__status=status_value)
        if development_stage:
            queryset = queryset.filter(sample__development_stage=development_stage)
        if test_order_no:
            queryset = queryset.filter(sample__test_order_no__icontains=test_order_no)
        if sample_no:
            queryset = queryset.filter(sample__sample_no__icontains=sample_no)
        if test_date_start and test_date_end:
            queryset = queryset.filter(test_date__range=[test_date_start, test_date_end])
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        serializer = SubstancesTestSerializer(page_obj, many=True)
        
        return Response.success(data={
            'results': serializer.data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'page_size': page_size
            }
        }, message="获取全谱检测数据成功")
        
    except Exception as e:
        return Response.error(message=f"获取全谱检测数据失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])
def substances_test_detail(request):
    """获取全谱检测明细数据"""
    try:
        test_id = request.GET.get('test_id')
        
        if not test_id:
            return Response.error(message="缺少test_id参数")
        
        try:
            substances_test = SubstancesTest.objects.get(id=test_id)
        except SubstancesTest.DoesNotExist:
            return Response.error(message="全谱检测数据不存在")
        
        details = SubstancesTestDetail.objects.filter(
            substances_test_id=test_id
        ).select_related('substance').order_by('id')
        
        serializer = SubstancesTestDetailSerializer(details, many=True)
        
        return Response.success(data=serializer.data, message="获取全谱物质明细成功")
        
    except Exception as e:
        return Response.error(message=f"获取全谱物质明细失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])
def substance_detail(request):
    """获取物质详细信息"""
    try:
        substance_id = request.GET.get('substance_id')
        
        if not substance_id:
            return Response.error(message="缺少substance_id参数")
        
        try:
            substance = Substance.objects.get(id=substance_id)
        except Substance.DoesNotExist:
            return Response.error(message="物质信息不存在")
        
        serializer = SubstanceSerializer(substance)
        
        return Response.success(data=serializer.data, message="获取物质详细信息成功")
        
    except Exception as e:
        return Response.error(message=f"获取物质详细信息失败: {str(e)}")
