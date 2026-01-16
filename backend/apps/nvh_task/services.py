"""
NVH Task 业务逻辑服务层
封装：提交/撤回/闭环刷新/校验
"""
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import (
    MainRecord, EntryExit, TestInfo, DocApproval, TestProcessAttachment,
    STATUS_DRAFT, STATUS_SUBMITTED
)


# ==================== 闭环刷新 ====================

def refresh_main_closed(main: MainRecord) -> MainRecord:
    """
    刷新单个 MainRecord 的闭环状态
    
    新闭环规则（按场景）：
    1) NORMAL（正常任务）：
       - doc_requirement=0: EE_OK && TI_OK
       - doc_requirement=1: EE_OK && TI_OK && DA_OK
    2) CANCEL_WITH_SAMPLE（取消且有样品）：
       - 仅需 EE_OK
    3) CANCEL_NO_SAMPLE（取消且无样品）：
       - 直接闭环 true
    
    表单 OK 口径：记录存在 && is_deleted=false && status=SUBMITTED
    """
    # 获取任务场景和技术资料要求
    task_scenario = main.task_scenario or "NORMAL"
    doc_requirement = main.doc_requirement
    
    # 判断 EntryExit 是否 OK
    entry_exit_ok = (
        main.entry_exit is not None
        and not main.entry_exit.is_deleted
        and main.entry_exit.status == STATUS_SUBMITTED
    )

    # 判断 TestInfo 是否 OK
    test_info_ok = False
    try:
        test_info = main.test_info
        if test_info and not test_info.is_deleted:
            test_info_ok = test_info.status == STATUS_SUBMITTED
    except TestInfo.DoesNotExist:
        pass

    # 判断 DocApproval 是否 OK
    doc_approval_ok = False
    try:
        doc_approval = main.doc_approval
        if doc_approval and not doc_approval.is_deleted:
            doc_approval_ok = doc_approval.status == STATUS_SUBMITTED
    except DocApproval.DoesNotExist:
        pass

    # 按场景计算闭环状态
    is_closed = False
    
    if task_scenario == "CANCEL_NO_SAMPLE":
        # 取消且无样品：直接闭环
        is_closed = True
    elif task_scenario == "CANCEL_WITH_SAMPLE":
        # 取消且有样品：仅需 EntryExit
        is_closed = entry_exit_ok
    else:
        # NORMAL 或其他场景：按 doc_requirement 判断
        if doc_requirement:
            # 要求技术资料：三表都需要
            is_closed = entry_exit_ok and test_info_ok and doc_approval_ok
        else:
            # 不要求技术资料：只需 EntryExit + TestInfo
            is_closed = entry_exit_ok and test_info_ok

    main.is_closed = is_closed
    main.closure_checked_at = timezone.now()
    main.save(update_fields=['is_closed', 'closure_checked_at'])

    return main


def refresh_mains_closed_by_entry_exit(entry_exit: EntryExit) -> int:
    """
    刷新所有引用该 EntryExit 的 MainRecord 的闭环状态
    返回刷新的记录数
    """
    count = 0
    for main in entry_exit.main_records.all():
        refresh_main_closed(main)
        count += 1
    return count


# ==================== EntryExit 提交/撤回 ====================

def validate_entry_exit_for_submit(entry_exit: EntryExit):
    """
    EntryExit 提交校验：关键字段最小校验
    必填字段：receiver_name, enter_time
    """
    errors = []
    if not entry_exit.receiver_name:
        errors.append("接收人不能为空")
    if not entry_exit.enter_time:
        errors.append("进入时间不能为空")
    if errors:
        raise ValidationError(errors)


def submit_entry_exit(entry_exit: EntryExit) -> EntryExit:
    """提交进出登记"""
    validate_entry_exit_for_submit(entry_exit)
    entry_exit.status = STATUS_SUBMITTED
    entry_exit.save(update_fields=['status', 'updated_at'])
    # 刷新所有引用该 EntryExit 的主任务闭环状态
    refresh_mains_closed_by_entry_exit(entry_exit)
    return entry_exit


def unsubmit_entry_exit(entry_exit: EntryExit) -> EntryExit:
    """撤回进出登记"""
    entry_exit.status = STATUS_DRAFT
    entry_exit.save(update_fields=['status', 'updated_at'])
    # 刷新所有引用该 EntryExit 的主任务闭环状态
    refresh_mains_closed_by_entry_exit(entry_exit)
    return entry_exit


# ==================== TestInfo 提交/撤回 ====================

def validate_test_info_for_submit(test_info: TestInfo):
    """
    TestInfo 提交校验：
    1) include_teardown_record == "是" → teardown_attachment_url 必须有
    2) include_process_record == "是" → 至少 1 条未软删 TestProcessAttachment
    3) report_required == "否" → report_no 必须为 "/"
    """
    errors = []

    # 校验1：拆装记录表
    if test_info.include_teardown_record == "是":
        if not test_info.teardown_attachment_url:
            errors.append("已勾选包含拆装记录表，必须上传拆装记录表附件")

    # 校验2：过程记录表
    if test_info.include_process_record == "是":
        attachment_count = TestProcessAttachment.objects.filter(
            test_info=test_info
        ).count()
        if attachment_count < 1:
            errors.append("已勾选包含试验过程记录表，至少需要上传1张过程记录表图片")


    if errors:
        raise ValidationError(errors)


def submit_test_info(test_info: TestInfo) -> TestInfo:
    """提交试验信息"""
    validate_test_info_for_submit(test_info)
    test_info.status = STATUS_SUBMITTED
    test_info.submitted_at = timezone.now()
    test_info.save(update_fields=['status', 'submitted_at', 'updated_at'])
    # 刷新主任务闭环状态
    refresh_main_closed(test_info.main)
    return test_info


def unsubmit_test_info(test_info: TestInfo) -> TestInfo:
    """撤回试验信息"""
    test_info.status = STATUS_DRAFT
    test_info.submitted_at = None
    test_info.save(update_fields=['status', 'submitted_at', 'updated_at'])
    # 刷新主任务闭环状态
    refresh_main_closed(test_info.main)
    return test_info


# ==================== DocApproval 提交/撤回 ====================

def validate_doc_approval_for_submit(doc: DocApproval):
    """
    DocApproval 提交校验：file_url 必须有
    """
    errors = []
    if not doc.file_url:
        errors.append("技术资料发放批准单必须上传文件")
    if errors:
        raise ValidationError(errors)


def submit_doc_approval(doc: DocApproval) -> DocApproval:
    """提交技术资料发放批准单"""
    validate_doc_approval_for_submit(doc)
    doc.status = STATUS_SUBMITTED
    doc.submitted_at = timezone.now()
    doc.save(update_fields=['status', 'submitted_at', 'updated_at'])
    # 刷新主任务闭环状态
    refresh_main_closed(doc.main)
    return doc


def unsubmit_doc_approval(doc: DocApproval) -> DocApproval:
    """撤回技术资料发放批准单"""
    doc.status = STATUS_DRAFT
    doc.submitted_at = None
    doc.save(update_fields=['status', 'submitted_at', 'updated_at'])
    # 刷新主任务闭环状态
    refresh_main_closed(doc.main)
    return doc
