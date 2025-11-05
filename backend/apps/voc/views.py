from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Max
from django.core.paginator import Paginator
from utils.response import Response
from .models import SampleInfo, VocOdorResult, SubstancesTest, SubstancesTestDetail, Substance
from .serializers import (
    VocOdorResultSerializer, VocQuerySerializer, VocChartDataSerializer,
    PartNameOptionSerializer, VehicleModelOptionSerializer, StatusOptionSerializer,
    SubstancesTestSerializer, SubstancesTestDetailSerializer, SubstanceSerializer,
    SubstancesQuerySerializer, ContributionTop25QuerySerializer,
    SubstanceItemTraceabilityQuerySerializer, SubstanceTraceabilityDetailSerializer
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
    """获取车型选项列表（用于物质溯源，返回整车数据组合）"""
    try:
        # 获取有整车全谱检测数据的样品信息，按车型+状态+开发阶段组合
        vehicle_samples = SampleInfo.objects.filter(
            part_name='整车',
            substancestest__isnull=False  # 确保有全谱检测数据
        ).select_related('vehicle_model').values(
            'vehicle_model_id',
            'vehicle_model__vehicle_model_name',
            'status',
            'development_stage'
        ).distinct().order_by('vehicle_model__vehicle_model_name', 'status', 'development_stage')
        
        # 构建选项列表：车型名称-检测状态-开发阶段
        options = []
        for item in vehicle_samples:
            vehicle_name = item['vehicle_model__vehicle_model_name']
            status = item['status'] or '未知状态'
            stage = item['development_stage'] or '未知阶段'
            
            options.append({
                'value': item['vehicle_model_id'],
                'label': f"{vehicle_name}-{status}-{stage}",
                'vehicle_model_id': item['vehicle_model_id'],
                'status': status,
                'development_stage': stage
            })
        
        return Response.success(data=options, message="获取车型选项成功")
        
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
            selected_compounds = ['benzene', 'toluene', 'ethylbenzene', 'formaldehyde', 'acetone', 'tvoc']
        
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
                           'formaldehyde', 'acetaldehyde', 'acrolein', 'acetone', 'tvoc']:
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
        
        # VOC物质平均值统计 前端未使用，如果统计需要可使用；未添加丙酮数据
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
        
        # X轴：固定物质（加入丙酮）
        x_axis = ["苯", "甲苯", "二甲苯", "乙苯", "苯乙烯", "甲醛", "乙醛", "丙酮", "TVOC"]
        compound_fields = ["benzene", "toluene", "xylene", "ethylbenzene", 
                          "styrene", "formaldehyde", "acetaldehyde", "acetone", "tvoc"]
        
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


@api_view(['GET'])
@permission_classes([])
def contribution_top25(request):
    """按项目（车型）输出GOi/GVi贡献度TOP25零部件"""
    try:
        # 校验参数：vehicle_model_id 或 vehicle_model_name 必须有其一
        query_serializer = ContributionTop25QuerySerializer(data=request.GET)
        query_serializer.is_valid(raise_exception=True)

        vehicle_model_id = query_serializer.validated_data.get('vehicle_model_id')
        vehicle_model_name = query_serializer.validated_data.get('vehicle_model_name')

        # 基础查询：过滤同项目（车型），排除“整车”，去除空零部件名
        queryset = SubstancesTest.objects.select_related('sample', 'sample__vehicle_model') \
            .exclude(sample__part_name="整车") \
            .exclude(sample__part_name__isnull=True) \
            .exclude(sample__part_name__exact="")

        if vehicle_model_id is not None:
            queryset = queryset.filter(sample__vehicle_model_id=vehicle_model_id)
        else:
            queryset = queryset.filter(sample__vehicle_model__vehicle_model_name=vehicle_model_name)

        # 唯一零部件数量及清单（基于SubstancesTest有记录的零部件）
        unique_part_names_qs = queryset.values_list('sample__part_name', flat=True).distinct()
        unique_part_names = list(unique_part_names_qs)
        unique_count = len(unique_part_names)

        # 数据量不足：仅返回提示信息与已存在的零部件清单，不返回榜单
        if unique_count < 35:
            msg = f"零部件数需≥35，当前项目仅有{unique_count}个零部件，数据不足"
            return Response.success(data={
                'vehicle_model_id': vehicle_model_id,
                'vehicle_model_name': vehicle_model_name,
                'parts_count': unique_count,
                'insufficient': True,
                'part_names': unique_part_names
            }, message=msg)

        # 生成 GOi TOP25
        goi_top = list(
            queryset.values('sample__part_name')
            .annotate(value=Max('goi'))
            .order_by('-value')[:25]
        )
        goi_top25 = [
            {
                'rank': idx + 1,
                'part_name': item['sample__part_name'],
                'goi': float(item['value']) if item['value'] is not None else None
            }
            for idx, item in enumerate(goi_top)
        ]

        # 生成 GVi TOP25
        gvi_top = list(
            queryset.values('sample__part_name')
            .annotate(value=Max('gvi'))
            .order_by('-value')[:25]
        )
        gvi_top25 = [
            {
                'rank': idx + 1,
                'part_name': item['sample__part_name'],
                'gvi': float(item['value']) if item['value'] is not None else None
            }
            for idx, item in enumerate(gvi_top)
        ]

        return Response.success(data={
            'vehicle_model_id': vehicle_model_id,
            'vehicle_model_name': vehicle_model_name,
            'parts_count': unique_count,
            'insufficient': False,
            'goi_top25': goi_top25,
            'gvi_top25': gvi_top25
        }, message="获取贡献度TOP25成功")

    except Exception as e:
        return Response.error(message=f"获取贡献度TOP25失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])
def substance_item_traceability(request):
    """物质分项溯源查询"""
    try:
        query_serializer = SubstanceItemTraceabilityQuerySerializer(data=request.GET)
        query_serializer.is_valid(raise_exception=True)
        
        vehicle_model_id = query_serializer.validated_data.get('vehicle_model_id')
        status = query_serializer.validated_data.get('status')
        development_stage = query_serializer.validated_data.get('development_stage')
        cas_nos = query_serializer.validated_data.get('cas_nos')
        
        # 1. 获取该车型整车样品的全谱检测数据（使用车型+状态+开发阶段精确匹配）
        vehicle_tests_query = SubstancesTest.objects.select_related('sample', 'sample__vehicle_model').filter(
            sample__vehicle_model_id=vehicle_model_id,
            sample__part_name='整车'
        )
        
        # 添加 status 和 development_stage 过滤条件
        if status:
            vehicle_tests_query = vehicle_tests_query.filter(sample__status=status)
        if development_stage:
            vehicle_tests_query = vehicle_tests_query.filter(sample__development_stage=development_stage)
        
        vehicle_tests = vehicle_tests_query
        
        if not vehicle_tests.exists():
            return Response.error(message="未找到匹配的整车全谱检测数据")
        
        # 取最新的整车检测数据（在满足条件的记录中选最新）
        vehicle_test = vehicle_tests.order_by('-test_date', '-id').first()
        
        # 2. 获取整车检测中选择物质的详细数据
        vehicle_details = SubstancesTestDetail.objects.select_related('substance').filter(
            substances_test=vehicle_test,
            substance__cas_no__in=cas_nos
        )
        
        if not vehicle_details.exists():
            return Response.error(message="未找到所选物质的整车检测数据")
        
        # 3. 获取所有零部件样品的全谱检测数据（排除整车）
        part_tests = SubstancesTest.objects.select_related('sample').filter(
            sample__vehicle_model_id=vehicle_model_id
        ).exclude(sample__part_name='整车')
        
        # 4. 获取所有零部件对这些物质的检测明细
        part_details = SubstancesTestDetail.objects.select_related(
            'substances_test__sample', 'substance'
        ).filter(
            substances_test__in=part_tests,
            substance__cas_no__in=cas_nos
        )
        
        # 5. 构建结果数据
        results = []
        
        for vehicle_detail in vehicle_details:
            substance = vehicle_detail.substance
            
            # 整车检测数据
            substance_data = {
                'substance_id': substance.id,
                'substance_name_cn': substance.substance_name_cn,
                'substance_name_en': substance.substance_name_en or '',
                'cas_no': substance.cas_no,
                'retention_time': float(vehicle_detail.retention_time) if vehicle_detail.retention_time else None,
                'match_degree': float(vehicle_detail.match_degree) if vehicle_detail.match_degree else None,
                'concentration_ratio': float(vehicle_detail.concentration_ratio) if vehicle_detail.concentration_ratio else None,
                'concentration': float(vehicle_detail.concentration) if vehicle_detail.concentration else None,
            }
            
            # 筛选该物质在零部件中的检测数据
            # 由于 SubstancesTestDetail.substance 现通过 cas_no 关联，d.substance_id 为 cas_no 字符串
            substance_part_details = [d for d in part_details if d.substance_id == substance.cas_no]
            
            # 按零件名称分组，计算平均值
            from collections import defaultdict
            part_data = defaultdict(lambda: {'qij_sum': 0, 'wih_sum': 0, 'concentration_sum': 0, 'count': 0})
            
            for detail in substance_part_details:
                part_name = detail.substances_test.sample.part_name
                if detail.dilution_oij is not None:
                    part_data[part_name]['qij_sum'] += float(detail.dilution_oij)
                if detail.dilution_wih is not None:
                    part_data[part_name]['wih_sum'] += float(detail.dilution_wih)
                if detail.concentration is not None:
                    part_data[part_name]['concentration_sum'] += float(detail.concentration)
                part_data[part_name]['count'] += 1
            
            # 计算每个零件的平均值
            part_averages = []
            for part_name, data in part_data.items():
                count = data['count']
                part_averages.append({
                    'part_name': part_name,
                    'qij_avg': data['qij_sum'] / count if count > 0 else 0,
                    'wih_avg': data['wih_sum'] / count if count > 0 else 0,
                    'concentration_avg': data['concentration_sum'] / count if count > 0 else 0
                })
            
            # 按Qij排序，取Top5（气味污染物来源）
            odor_top5_data = sorted(part_averages, key=lambda x: x['qij_avg'], reverse=True)[:5]
            odor_top5 = []
            for idx, item in enumerate(odor_top5_data):
                odor_top5.append({
                    'rank': idx + 1,
                    'part_name': item['part_name'],
                    'qij': round(item['qij_avg'], 2) if item['qij_avg'] > 0 else None,
                    'concentration': round(item['concentration_avg'], 3) if item['concentration_avg'] > 0 else None
                })
            
            # 补足5个位置（如果不足）
            while len(odor_top5) < 5:
                odor_top5.append({
                    'rank': len(odor_top5) + 1,
                    'part_name': None,
                    'qij': None,
                    'concentration': None
                })
            
            # 按Wih排序，取Top5（有机污染物来源）
            organic_top5_data = sorted(part_averages, key=lambda x: x['wih_avg'], reverse=True)[:5]
            organic_top5 = []
            for idx, item in enumerate(organic_top5_data):
                organic_top5.append({
                    'rank': idx + 1,
                    'part_name': item['part_name'],
                    'wih': round(item['wih_avg'], 2) if item['wih_avg'] > 0 else None,
                    'concentration': round(item['concentration_avg'], 3) if item['concentration_avg'] > 0 else None
                })
            
            # 补足5个位置（如果不足）
            while len(organic_top5) < 5:
                organic_top5.append({
                    'rank': len(organic_top5) + 1,
                    'part_name': None,
                    'wih': None,
                    'concentration': None
                })
            
            substance_data['odor_top5'] = odor_top5
            substance_data['organic_top5'] = organic_top5
            
            results.append(substance_data)
        
        # 序列化返回
        serializer = SubstanceTraceabilityDetailSerializer(results, many=True)
        
        return Response.success(data={
            'vehicle_model_id': vehicle_model_id,
            'substances': serializer.data
        }, message="获取物质分项溯源数据成功")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response.error(message=f"获取物质分项溯源数据失败: {str(e)}")
