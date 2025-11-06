from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.core.paginator import Paginator
from django.db.models import Q

from utils.response import Response
from .models import SampleInfo
from .serializers import VocOdorDataSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def data_list(request):
    """获取VOC/气味数据列表（基于新SampleInfo，兼容旧前端所需结构）"""
    try:
        page = int(request.GET.get('page', 1) or 1)
        page_size = int(request.GET.get('page_size', 10) or 10)

        queryset = SampleInfo.objects.all().order_by('-id')

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = VocOdorDataSerializer(page_obj, many=True)
        return Response.success(data={
            'results': serializer.data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'page_size': page_size
            }
        }, message='获取数据成功')
    except Exception as e:
        return Response.error(message=f'获取数据失败: {str(e)}')


@api_view(['GET'])
@permission_classes([AllowAny])
def project_name_options(request):
    """获取项目名称选项（整车 + 有全量信息时优先），label: 项目-状态-阶段，value: 项目名称"""
    try:
        # 基于整车样品构建组合选项
        base_qs = SampleInfo.objects.filter(part_name='整车') \
            .values('project_name', 'status', 'development_stage') \
            .distinct().order_by('project_name', 'status', 'development_stage')

        options = []
        for item in base_qs:
            project = item['project_name']
            status = item['status'] or '未知状态'
            stage = item['development_stage'] or '未知阶段'
            options.append({
                'value': project,
                'label': f"{project}-{status}-{stage}",
                'project_name': project,
                'status': status,
                'development_stage': stage
            })

        # 若没有整车数据，则退化为所有项目名去重
        if not options:
            all_projects = SampleInfo.objects.values_list('project_name', flat=True).distinct()
            options = [{'value': p, 'label': p} for p in all_projects if p]

        return Response.success(data=options, message='获取项目名称选项成功')
    except Exception as e:
        return Response.error(message=f'获取项目名称选项失败: {str(e)}')


def _apply_filters(qs, filters):
    project_names = filters.get('project_names', []) or []
    if project_names:
        qs = qs.filter(project_name__in=project_names)

    part_names = filters.get('part_names', []) or []
    if part_names:
        qs = qs.filter(part_name__in=part_names)

    statuses = filters.get('statuses', []) or []
    if statuses:
        qs = qs.filter(status__in=statuses)

    development_stages = filters.get('development_stages', []) or []
    if development_stages:
        qs = qs.filter(development_stage__in=development_stages)

    test_order_no = filters.get('test_order_no') or ''
    if test_order_no:
        qs = qs.filter(test_order_no__icontains=test_order_no)

    sample_no = filters.get('sample_no') or ''
    if sample_no:
        qs = qs.filter(sample_no__icontains=sample_no)

    test_date_range = filters.get('test_date_range') or []
    if isinstance(test_date_range, (list, tuple)) and len(test_date_range) == 2:
        qs = qs.filter(test_date__range=test_date_range)

    return qs


@api_view(['GET'])
@permission_classes([AllowAny])
def row_chart_data(request):
    """单行VOC图表数据（基于样品ID）"""
    try:
        result_id = request.GET.get('result_id')
        if not result_id:
            return Response.error(message='缺少result_id参数')

        try:
            current = SampleInfo.objects.get(id=result_id)
        except SampleInfo.DoesNotExist:
            return Response.error(message='数据不存在')

        project = current.project_name
        is_whole_vehicle = (current.part_name == '整车')

        if is_whole_vehicle:
            queryset = SampleInfo.objects.filter(project_name=project, part_name='整车')
        else:
            queryset = SampleInfo.objects.filter(project_name=project, part_name=current.part_name)

        x_axis = ["苯", "甲苯", "二甲苯", "乙苯", "苯乙烯", "甲醛", "乙醛", "丙酮", "TVOC"]
        fields = ["benzene", "toluene", "xylene", "ethylbenzene",
                  "styrene", "formaldehyde", "acetaldehyde", "acetone", "tvoc"]

        series_map = {}
        for s in queryset:
            if is_whole_vehicle:
                series_name = f"{s.status or '未知'}-{s.development_stage or '未知'}"
            else:
                series_name = f"{s.part_name or '未知'}-{s.development_stage or '未知'}"

            values = [float(getattr(s, f) or 0) for f in fields]
            if series_name not in series_map:
                series_map[series_name] = {
                    'name': series_name,
                    'data': values,
                    'type': 'bar'
                }

        return Response.success(data={
            'xAxis': x_axis,
            'series': list(series_map.values()),
            'scenario': 'whole_vehicle' if is_whole_vehicle else 'part',
            'project_name': project,
            'part_name': current.part_name
        }, message='获取图表数据成功')
    except Exception as e:
        return Response.error(message=f'获取图表数据失败: {str(e)}')


@api_view(['POST'])
@permission_classes([AllowAny])
def filtered_voc_chart_data(request):
    """基于筛选条件的VOC图表数据"""
    try:
        filters = request.data.get('filters', {}) or {}
        limit = int(request.data.get('limit', 10) or 10)

        queryset = SampleInfo.objects.all()
        queryset = _apply_filters(queryset, filters)
        queryset = queryset.order_by('-id')[:limit]

        x_axis = ["苯", "甲苯", "二甲苯", "乙苯", "苯乙烯", "甲醛", "乙醛", "丙酮", "TVOC"]
        fields = ["benzene", "toluene", "xylene", "ethylbenzene",
                  "styrene", "formaldehyde", "acetaldehyde", "acetone", "tvoc"]

        series = []
        for s in queryset:
            values = [float(getattr(s, f) or 0) for f in fields]
            series.append({
                'name': f"{s.project_name}-{s.sample_no}",
                'data': values,
                'type': 'bar',
                'part_name': s.part_name,
                'raw_data': {
                    'vehicle_model': s.project_name,
                    'sample_no': s.sample_no,
                    'status': s.status,
                    'stage': s.development_stage
                }
            })

        is_whole_vehicle = all((it.get('part_name') == '整车') for it in series) if series else False
        return Response.success(data={
            'xAxis': x_axis,
            'series': series,
            'scenario': 'whole_vehicle' if is_whole_vehicle else 'part'
        }, message='获取图表数据成功')
    except Exception as e:
        return Response.error(message=f'获取图表数据失败: {str(e)}')


@api_view(['GET'])
@permission_classes([AllowAny])
def odor_row_chart_data(request):
    """单行气味图表数据（基于样品ID）"""
    try:
        result_id = request.GET.get('result_id')
        if not result_id:
            return Response.error(message='缺少result_id参数')

        try:
            current = SampleInfo.objects.get(id=result_id)
        except SampleInfo.DoesNotExist:
            return Response.error(message='数据不存在')

        project = current.project_name
        is_whole_vehicle = (current.part_name == '整车')

        if is_whole_vehicle:
            queryset = SampleInfo.objects.filter(project_name=project, part_name='整车')
            x_axis = ["动态-前排", "动态-后排", "静态-前排", "静态-后排", "气味均值"]
            fields = ["odor_dynamic_front", "odor_dynamic_rear", "odor_static_front", "odor_static_rear", "odor_mean"]
        else:
            queryset = SampleInfo.objects.filter(project_name=project, part_name=current.part_name)
            x_axis = ["气味均值"]
            fields = ["odor_mean"]

        series_map = {}
        for s in queryset:
            if is_whole_vehicle:
                series_name = f"{project}-{s.development_stage or '未知'}"
            else:
                series_name = f"{current.part_name}-{s.development_stage or '未知'}"

            values = [float(getattr(s, f) or 0) for f in fields]
            if series_name not in series_map:
                series_map[series_name] = {
                    'name': series_name,
                    'data': values,
                    'type': 'bar'
                }

        return Response.success(data={
            'xAxis': x_axis,
            'series': list(series_map.values()),
            'scenario': 'whole_vehicle' if is_whole_vehicle else 'part'
        }, message='获取图表数据成功')
    except Exception as e:
        return Response.error(message=f'获取图表数据失败: {str(e)}')


@api_view(['POST'])
@permission_classes([AllowAny])
def filtered_odor_chart_data(request):
    """基于筛选条件的气味图表数据"""
    try:
        filters = request.data.get('filters', {}) or {}
        limit = int(request.data.get('limit', 10) or 10)

        queryset = SampleInfo.objects.all()
        queryset = _apply_filters(queryset, filters)
        queryset = queryset.order_by('-id')[:limit]

        # 气味图采用固定5项（与旧端一致）
        x_axis = ["动态-前排", "动态-后排", "静态-前排", "静态-后排", "气味均值"]
        fields = ["odor_dynamic_front", "odor_dynamic_rear", "odor_static_front", "odor_static_rear", "odor_mean"]

        series = []
        for s in queryset:
            values = [float(getattr(s, f) or 0) for f in fields]
            series.append({
                'name': f"{s.project_name}-{s.sample_no}",
                'data': values,
                'type': 'bar',
                'part_name': s.part_name,
                'raw_data': {
                    'vehicle_model': s.project_name,
                    'sample_no': s.sample_no,
                    'status': s.status,
                    'stage': s.development_stage
                }
            })

        return Response.success(data={
            'xAxis': x_axis,
            'series': series
        }, message='获取图表数据成功')
    except Exception as e:
        return Response.error(message=f'获取图表数据失败: {str(e)}')

