"""
NVH Task Views
"""
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from utils.response import Response
from .models import (
    MainRecord, EntryExit, TestInfo, DocApproval,
    TestProcessAttachment, TestProcessList, STATUS_DRAFT
)
from .serializers import (
    MainRecordListSerializer, MainRecordDetailSerializer, MainRecordCreateUpdateSerializer,
    EntryExitSerializer, TestInfoSerializer, DocApprovalSerializer,
    TestProcessAttachmentSerializer, TestProcessListSerializer
)
from . import services


# ==================== 分页工具 ====================

def get_pagination_params(request):
    """获取分页参数"""
    try:
        page = int(request.GET.get('page', '1'))
    except (ValueError, TypeError):
        page = 1

    default_page_size = getattr(settings, 'REST_FRAMEWORK', {}).get('PAGE_SIZE', 20)
    try:
        page_size = int(request.GET.get('page_size', str(default_page_size)))
    except (ValueError, TypeError):
        page_size = default_page_size

    return max(1, page), max(1, min(page_size, 100))


def paginate_queryset(queryset, page, page_size):
    """分页查询集"""
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    items = queryset[start:end]
    return items, total


# ==================== MainRecord 视图 ====================

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def main_record_list(request):
    """主记录列表（含筛选）/ 创建"""
    if request.method == 'GET':
        queryset = MainRecord.objects.select_related(
            'entry_exit', 'test_info', 'doc_approval'
        ).order_by('-schedule_start', '-id')

        # 筛选：车型
        model_filter = request.GET.get('model')
        if model_filter:
            queryset = queryset.filter(model__icontains=model_filter)

        # 筛选：VIN/零件编号
        vin = request.GET.get('vin_or_part_no')
        if vin:
            queryset = queryset.filter(vin_or_part_no__icontains=vin)

        # 筛选：试验名称
        test_name = request.GET.get('test_name')
        if test_name:
            queryset = queryset.filter(test_name__icontains=test_name)

        # 筛选：加入预警系统状态
        warning_status = request.GET.get('warning_system_status')
        if warning_status:
            queryset = queryset.filter(warning_system_status=warning_status)

        # 筛选：合同编号
        contract_no = request.GET.get('contract_no')
        if contract_no:
            queryset = queryset.filter(contract_no__icontains=contract_no)

        # 筛选：任务提出人
        requester = request.GET.get('requester_name')
        if requester:
            queryset = queryset.filter(requester_name__icontains=requester)

        # 筛选：测试人员
        tester = request.GET.get('tester_name')
        if tester:
            queryset = queryset.filter(tester_name__icontains=tester)

        # 筛选：是否闭环
        is_closed = request.GET.get('is_closed')
        if is_closed is not None and is_closed != '':
            queryset = queryset.filter(is_closed=(is_closed.lower() in ['true', '1', 'yes']))

        # 筛选：时间范围
        start_date = request.GET.get('schedule_start_from')
        end_date = request.GET.get('schedule_start_to')
        if start_date:
            queryset = queryset.filter(schedule_start__gte=start_date)
        if end_date:
            queryset = queryset.filter(schedule_start__lte=end_date)

        # 分页
        page, page_size = get_pagination_params(request)
        items, total = paginate_queryset(queryset, page, page_size)

        serializer = MainRecordListSerializer(items, many=True)
        return Response.success(
            data={
                'items': serializer.data,
                'total': total,
                'page': page,
                'page_size': page_size,
            },
            message='获取任务列表成功'
        )

    # POST 创建
    serializer = MainRecordCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        output = MainRecordDetailSerializer(instance).data
        return Response.success(data=output, message='创建任务成功', status_code=201)
    return Response.bad_request(message='创建任务失败', data=serializer.errors)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def main_record_detail(request, pk):
    """主记录详情 / 更新 / 删除"""
    try:
        instance = MainRecord.objects.select_related(
            'entry_exit', 'test_info', 'doc_approval'
        ).get(pk=pk)
    except MainRecord.DoesNotExist:
        return Response.not_found(message='任务不存在')

    if request.method == 'GET':
        serializer = MainRecordDetailSerializer(instance)
        return Response.success(data=serializer.data, message='获取任务详情成功')

    if request.method == 'PATCH':
        old_entry_exit_id = instance.entry_exit_id
        serializer = MainRecordCreateUpdateSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            # 检查 entry_exit_id 是否变化，触发闭环刷新
            if 'entry_exit_id' in request.data:
                new_entry_exit_id = instance.entry_exit_id
                if old_entry_exit_id != new_entry_exit_id:
                    services.refresh_main_closed(instance)
            output = MainRecordDetailSerializer(instance).data
            return Response.success(data=output, message='更新任务成功')
        return Response.bad_request(message='更新任务失败', data=serializer.errors)

    if request.method == 'DELETE':
        instance.soft_delete()
        return Response.success(message='删除任务成功')


# ==================== EntryExit 视图 ====================

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def entry_exit_list(request):
    """进出登记列表 / 创建"""
    if request.method == 'GET':
        queryset = EntryExit.objects.order_by('-created_at', '-id')

        # 筛选：状态
        status_filter = request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # 筛选：接收人
        receiver = request.GET.get('receiver_name')
        if receiver:
            queryset = queryset.filter(receiver_name__icontains=receiver)

        page, page_size = get_pagination_params(request)
        items, total = paginate_queryset(queryset, page, page_size)

        serializer = EntryExitSerializer(items, many=True)
        return Response.success(
            data={
                'items': serializer.data,
                'total': total,
                'page': page,
                'page_size': page_size,
            },
            message='获取进出登记列表成功'
        )

    # POST 创建
    serializer = EntryExitSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        output = EntryExitSerializer(instance).data
        return Response.success(data=output, message='创建进出登记成功', status_code=201)
    return Response.bad_request(message='创建进出登记失败', data=serializer.errors)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def entry_exit_detail(request, pk):
    """进出登记详情 / 更新 / 删除"""
    try:
        instance = EntryExit.objects.get(pk=pk)
    except EntryExit.DoesNotExist:
        return Response.not_found(message='进出登记不存在')

    if request.method == 'GET':
        serializer = EntryExitSerializer(instance)
        return Response.success(data=serializer.data, message='获取进出登记详情成功')

    if request.method == 'PATCH':
        serializer = EntryExitSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            output = EntryExitSerializer(instance).data
            return Response.success(data=output, message='更新进出登记成功')
        return Response.bad_request(message='更新进出登记失败', data=serializer.errors)

    if request.method == 'DELETE':
        try:
            instance.soft_delete()
            return Response.success(message='删除进出登记成功')
        except DjangoValidationError as e:
            return Response.bad_request(message=str(e.messages[0]) if e.messages else '删除失败')


@api_view(['POST'])
@permission_classes([AllowAny])
def entry_exit_submit(request, pk):
    """提交进出登记"""
    try:
        instance = EntryExit.objects.get(pk=pk)
    except EntryExit.DoesNotExist:
        return Response.not_found(message='进出登记不存在')

    try:
        services.submit_entry_exit(instance)
        output = EntryExitSerializer(instance).data
        return Response.success(data=output, message='提交成功')
    except DjangoValidationError as e:
        return Response.bad_request(message='提交失败', data=e.messages)


@api_view(['POST'])
@permission_classes([AllowAny])
def entry_exit_unsubmit(request, pk):
    """撤回进出登记"""
    try:
        instance = EntryExit.objects.get(pk=pk)
    except EntryExit.DoesNotExist:
        return Response.not_found(message='进出登记不存在')

    services.unsubmit_entry_exit(instance)
    output = EntryExitSerializer(instance).data
    return Response.success(data=output, message='撤回成功')


# ==================== TestInfo 视图 ====================

@api_view(['GET', 'PATCH'])
@permission_classes([AllowAny])
def test_info_by_main(request, main_id):
    """获取或创建主记录的试验信息（get_or_create）"""
    try:
        main = MainRecord.objects.get(pk=main_id)
    except MainRecord.DoesNotExist:
        return Response.not_found(message='主任务不存在')

    if request.method == 'GET':
        instance, created = TestInfo.objects.get_or_create(
            main=main,
            defaults={'status': STATUS_DRAFT}
        )
        serializer = TestInfoSerializer(instance)
        return Response.success(data=serializer.data, message='获取试验信息成功')

    if request.method == 'PATCH':
        try:
            instance = TestInfo.objects.get(main=main)
        except TestInfo.DoesNotExist:
            return Response.not_found(message='试验信息不存在，请先GET创建')

        serializer = TestInfoSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            output = TestInfoSerializer(instance).data
            return Response.success(data=output, message='更新试验信息成功')
        return Response.bad_request(message='更新试验信息失败', data=serializer.errors)


@api_view(['POST'])
@permission_classes([AllowAny])
def test_info_submit(request, pk):
    """提交试验信息"""
    try:
        instance = TestInfo.objects.get(pk=pk)
    except TestInfo.DoesNotExist:
        return Response.not_found(message='试验信息不存在')

    try:
        services.submit_test_info(instance)
        output = TestInfoSerializer(instance).data
        return Response.success(data=output, message='提交成功')
    except DjangoValidationError as e:
        return Response.bad_request(message='提交失败', data=e.messages)


@api_view(['POST'])
@permission_classes([AllowAny])
def test_info_unsubmit(request, pk):
    """撤回试验信息"""
    try:
        instance = TestInfo.objects.get(pk=pk)
    except TestInfo.DoesNotExist:
        return Response.not_found(message='试验信息不存在')

    services.unsubmit_test_info(instance)
    output = TestInfoSerializer(instance).data
    return Response.success(data=output, message='撤回成功')


# ==================== DocApproval 视图 ====================

@api_view(['GET', 'PATCH'])
@permission_classes([AllowAny])
def doc_approval_by_main(request, main_id):
    """获取或创建主记录的技术资料发放批准单（get_or_create）"""
    try:
        main = MainRecord.objects.get(pk=main_id)
    except MainRecord.DoesNotExist:
        return Response.not_found(message='主任务不存在')

    if request.method == 'GET':
        instance, created = DocApproval.objects.get_or_create(
            main=main,
            defaults={'status': STATUS_DRAFT}
        )
        serializer = DocApprovalSerializer(instance)
        return Response.success(data=serializer.data, message='获取技术资料批准单成功')

    if request.method == 'PATCH':
        try:
            instance = DocApproval.objects.get(main=main)
        except DocApproval.DoesNotExist:
            return Response.not_found(message='技术资料批准单不存在，请先GET创建')

        serializer = DocApprovalSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            output = DocApprovalSerializer(instance).data
            return Response.success(data=output, message='更新技术资料批准单成功')
        return Response.bad_request(message='更新技术资料批准单失败', data=serializer.errors)


@api_view(['POST'])
@permission_classes([AllowAny])
def doc_approval_submit(request, pk):
    """提交技术资料发放批准单"""
    try:
        instance = DocApproval.objects.get(pk=pk)
    except DocApproval.DoesNotExist:
        return Response.not_found(message='技术资料批准单不存在')

    try:
        services.submit_doc_approval(instance)
        output = DocApprovalSerializer(instance).data
        return Response.success(data=output, message='提交成功')
    except DjangoValidationError as e:
        return Response.bad_request(message='提交失败', data=e.messages)


@api_view(['POST'])
@permission_classes([AllowAny])
def doc_approval_unsubmit(request, pk):
    """撤回技术资料发放批准单"""
    try:
        instance = DocApproval.objects.get(pk=pk)
    except DocApproval.DoesNotExist:
        return Response.not_found(message='技术资料批准单不存在')

    services.unsubmit_doc_approval(instance)
    output = DocApprovalSerializer(instance).data
    return Response.success(data=output, message='撤回成功')


# ==================== TestProcessAttachment 视图 ====================

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def process_attachment_list(request):
    """过程记录附件列表 / 创建"""
    if request.method == 'GET':
        test_info_id = request.GET.get('test_info_id')
        if not test_info_id:
            return Response.bad_request(message='缺少 test_info_id 参数')

        queryset = TestProcessAttachment.objects.filter(
            test_info_id=test_info_id
        ).order_by('sort_no', 'id')

        serializer = TestProcessAttachmentSerializer(queryset, many=True)
        return Response.success(data=serializer.data, message='获取过程记录附件列表成功')

    # POST 创建
    serializer = TestProcessAttachmentSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        output = TestProcessAttachmentSerializer(instance).data
        return Response.success(data=output, message='创建过程记录附件成功', status_code=201)
    return Response.bad_request(message='创建过程记录附件失败', data=serializer.errors)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def process_attachment_detail(request, pk):
    """过程记录附件详情 / 更新 / 删除"""
    try:
        instance = TestProcessAttachment.objects.get(pk=pk)
    except TestProcessAttachment.DoesNotExist:
        return Response.not_found(message='过程记录附件不存在')

    if request.method == 'GET':
        serializer = TestProcessAttachmentSerializer(instance)
        return Response.success(data=serializer.data, message='获取过程记录附件详情成功')

    if request.method == 'PATCH':
        serializer = TestProcessAttachmentSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            output = TestProcessAttachmentSerializer(instance).data
            return Response.success(data=output, message='更新过程记录附件成功')
        return Response.bad_request(message='更新过程记录附件失败', data=serializer.errors)

    if request.method == 'DELETE':
        instance.soft_delete()
        return Response.success(message='删除过程记录附件成功')


# ==================== TestProcessList 视图 ====================

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def process_list_options(request):
    """过程记录表名字典列表 / 新增"""
    if request.method == 'GET':
        queryset = TestProcessList.objects.order_by('id')
        serializer = TestProcessListSerializer(queryset, many=True)
        return Response.success(data=serializer.data, message='获取过程记录表名列表成功')

    # POST 创建（支持输入即新增）
    serializer = TestProcessListSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        output = TestProcessListSerializer(instance).data
        return Response.success(data=output, message='创建过程记录表名成功', status_code=201)
    return Response.bad_request(message='创建过程记录表名失败', data=serializer.errors)


# ==================== 图片上传视图 ====================

import os
import uuid
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser


ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_image(request):
    """
    通用图片上传接口
    支持上传到不同目录：teardown_record / nvh_test_process / nvh_task_approval
    """
    file = request.FILES.get('file')
    upload_type = request.POST.get('type', 'nvh_test_process')  # 默认过程记录

    if not file:
        return Response.bad_request(message='未选择文件')

    # 校验文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        return Response.bad_request(message=f'不支持的文件类型: {file.content_type}，仅支持 jpg/png/webp/gif')

    # 校验文件大小
    if file.size > MAX_FILE_SIZE:
        return Response.bad_request(message=f'文件大小超过限制（最大 5MB）')

    # 确定保存目录
    type_to_dir = {
        'teardown_record': 'nvh_task/teardown_record',
        'nvh_test_process': 'nvh_task/nvh_test_process',
        'nvh_task_approval': 'nvh_task/nvh_task_approval',
    }
    sub_dir = type_to_dir.get(upload_type, 'nvh_task/nvh_test_process')

    # 生成唯一文件名
    ext = os.path.splitext(file.name)[1].lower()
    if not ext:
        ext = '.jpg'
    new_filename = f"{uuid.uuid4().hex}{ext}"

    # 完整保存路径
    save_dir = os.path.join(settings.MEDIA_ROOT, sub_dir)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, new_filename)

    # 保存文件
    try:
        with open(save_path, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)
    except Exception as e:
        return Response.error(message=f'文件保存失败: {str(e)}')

    # 返回相对路径（相对于 MEDIA_ROOT）
    relative_path = f"{sub_dir}/{new_filename}"
    full_url = f"{settings.MEDIA_URL}{relative_path}"

    return Response.success(
        data={
            'relative_path': relative_path,
            'url': full_url,
            'filename': new_filename,
        },
        message='上传成功'
    )
