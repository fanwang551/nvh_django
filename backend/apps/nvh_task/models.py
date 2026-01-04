from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError


# ==================== 软删除基类 ====================

class SoftDeleteQuerySet(models.QuerySet):
    """支持软删除的 QuerySet"""

    def delete(self):
        """QuerySet 批量删除时，默认做软删除"""
        return super().update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        """物理删除（一般不用）"""
        return super().delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """默认只返回未删除数据"""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    """软删除抽象基类，所有业务模型必须继承"""

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()     # 默认过滤 is_deleted=False
    all_objects = models.Manager()    # 可查询全部（含已删除）

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """兜底：任何地方调用 instance.delete() 也走软删除"""
        return self.soft_delete(using=using, keep_parents=keep_parents)

    def soft_delete(self, using=None, keep_parents=False):
        """实例软删除"""
        if self.is_deleted:
            return
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        """恢复（如将来需要）"""
        if not self.is_deleted:
            return
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        """物理删除（一般不用）"""
        return super().delete(using=using, keep_parents=keep_parents)


# ==================== 状态常量 ====================

STATUS_DRAFT = "DRAFT"
STATUS_SUBMITTED = "SUBMITTED"


# ==================== 业务模型 ====================

class EntryExit(SoftDeleteModel):
    """车辆及零件进出登记（可被多个 MainRecord 共用）"""

    receiver_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="接收人")
    enter_time = models.DateTimeField(null=True, blank=True, verbose_name="进入时间")
    purpose = models.CharField(max_length=100, null=True, blank=True, default="测试", verbose_name="用途")

    dispose_type = models.CharField(max_length=20, null=True, blank=True, verbose_name="报废/归还类型")
    disposer_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="报废/归还人姓名")
    dispose_time = models.DateTimeField(null=True, blank=True, verbose_name="报废/归还时间")
    return_receiver = models.CharField(max_length=100, null=True, blank=True, verbose_name="归还接受人")

    remark = models.CharField(max_length=1000, null=True, blank=True, verbose_name="备注")
    status = models.CharField(max_length=20, default=STATUS_DRAFT, db_index=True, verbose_name="表单状态")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "车辆及零件进出登记"
        verbose_name_plural = "车辆及零件进出登记"

    def __str__(self):
        return f"EntryExit#{self.id}"

    def active_mainrecord_count(self) -> int:
        """返回引用此进出登记的未删除主记录数量"""
        return self.main_records.count()

    def soft_delete(self, using=None, keep_parents=False):
        """进出登记软删除：被多条任务引用时阻止删除"""
        if self.active_mainrecord_count() > 1:
            raise ValidationError("该进出登记被多条任务引用，不能删除。请先解绑或仅保留一条引用。")
        return super().soft_delete(using=using, keep_parents=keep_parents)


class MainRecord(SoftDeleteModel):
    """任务主记录"""

    model = models.CharField(max_length=100, verbose_name="车型")
    vin_or_part_no = models.CharField(max_length=100, db_index=True, verbose_name="VIN码/零件编号")
    test_name = models.CharField(max_length=200, verbose_name="试验名称")

    warning_system_status = models.CharField(max_length=20, verbose_name="加入预警系统状态")

    requester_name = models.CharField(max_length=100, verbose_name="任务提出人")
    schedule_start = models.DateTimeField(db_index=True, verbose_name="试验安排开始时间")
    schedule_end = models.DateTimeField(null=True, blank=True, verbose_name="试验安排结束时间")
    schedule_remark = models.CharField(max_length=500, null=True, blank=True, verbose_name="试验安排时间备注")
    test_location = models.CharField(max_length=200, null=True, blank=True, verbose_name="试验地点")

    tester_name = models.CharField(max_length=100, verbose_name="测试人员")
    contract_no = models.CharField(max_length=100, null=True, blank=True, db_index=True, verbose_name="合同编号")
    remark = models.CharField(max_length=1000, null=True, blank=True, verbose_name="备注")

    entry_exit = models.ForeignKey(
        "EntryExit",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="main_records",
        verbose_name="关联进出登记",
    )

    is_closed = models.BooleanField(default=False, db_index=True, verbose_name="是否闭环")
    closure_checked_at = models.DateTimeField(null=True, blank=True, verbose_name="闭环判断更新时间")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "任务主记录"
        verbose_name_plural = "任务主记录"

    def __str__(self):
        return f"MainRecord#{self.id} {self.vin_or_part_no} {self.test_name}"

    def soft_delete(self, using=None, keep_parents=False):
        """
        主记录软删除策略：
        - 不动 EntryExit（共享）
        - 同步软删除 OneToOne：TestInfo、DocApproval
        """
        with transaction.atomic():
            if hasattr(self, "test_info") and self.test_info and not self.test_info.is_deleted:
                self.test_info.soft_delete()
            if hasattr(self, "doc_approval") and self.doc_approval and not self.doc_approval.is_deleted:
                self.doc_approval.soft_delete()
            return super().soft_delete(using=using, keep_parents=keep_parents)


class TestInfo(SoftDeleteModel):
    """试验信息登记（与 MainRecord 一对一）"""

    main = models.OneToOneField(
        "MainRecord",
        on_delete=models.CASCADE,
        related_name="test_info",
        verbose_name="关联主任务",
    )

    contact_phone = models.CharField(max_length=50, null=True, blank=True, verbose_name="联系方式")
    nvh_lab_mgmt_no = models.CharField(max_length=100, null=True, blank=True, db_index=True, verbose_name="NVH试验室管理号")

    sample_type = models.CharField(max_length=20, null=True, blank=True, verbose_name="样品名称")
    rd_stage = models.CharField(max_length=20, null=True, blank=True, verbose_name="研发阶段")
    delivery_dept = models.CharField(max_length=200, null=True, blank=True, verbose_name="送件部门")

    report_required = models.CharField(max_length=20, null=True, blank=True, verbose_name="是否出具试验/不确定度报告")
    report_no = models.CharField(max_length=100, default="/", verbose_name="报告编号")

    include_teardown_record = models.CharField(max_length=20, default="否", verbose_name="是否包含拆装记录表")
    include_process_record = models.CharField(max_length=20, default="否", verbose_name="是否包含试验过程记录表")

    teardown_attachment_url = models.ImageField(
        upload_to='nvh_task/teardown_record/',
        null=True, blank=True,
        verbose_name="拆装记录表附件(图片)"
    )

    status = models.CharField(max_length=20, default=STATUS_DRAFT, db_index=True, verbose_name="表单状态")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="提交时间")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "试验信息登记"
        verbose_name_plural = "试验信息登记"

    def __str__(self):
        return f"TestInfo(main_id={self.main_id})"

    def soft_delete(self, using=None, keep_parents=False):
        """试验信息软删除：级联软删除所有过程附件"""
        with transaction.atomic():
            TestProcessAttachment.all_objects.filter(
                test_info_id=self.id, is_deleted=False
            ).update(is_deleted=True, deleted_at=timezone.now())
            return super().soft_delete(using=using, keep_parents=keep_parents)


class TestProcessAttachment(SoftDeleteModel):
    """试验过程记录附件"""

    test_info = models.ForeignKey(
        "TestInfo",
        on_delete=models.CASCADE,
        related_name="process_attachments",
        verbose_name="关联试验信息",
    )
    record_name = models.CharField(max_length=200, verbose_name="过程记录表名")

    file_url = models.ImageField(
        upload_to='nvh_task/nvh_test_process/',
        verbose_name="图片(过程记录附件)"
    )

    sort_no = models.PositiveIntegerField(default=0, verbose_name="排序号")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "试验过程记录附件"
        verbose_name_plural = "试验过程记录附件"

    def __str__(self):
        return f"TestProcessAttachment#{self.id} {self.record_name}"


class TestProcessList(SoftDeleteModel):
    """试验过程记录表清单（字典表，用于下拉选择）"""

    test_process_name = models.CharField(max_length=200, verbose_name="过程记录表名")

    class Meta:
        verbose_name = "试验过程记录表清单"
        verbose_name_plural = "试验过程记录表清单"

    def __str__(self):
        return self.test_process_name


class DocApproval(SoftDeleteModel):
    """技术资料发放批准单（与 MainRecord 一对一）"""

    main = models.OneToOneField(
        "MainRecord",
        on_delete=models.CASCADE,
        related_name="doc_approval",
        verbose_name="关联主任务",
    )

    doc_name = models.CharField(max_length=200, null=True, blank=True, verbose_name="名称")
    doc_no = models.CharField(max_length=100, null=True, blank=True, verbose_name="编号")
    quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name="数量")

    receiver_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="接收人")
    issuer_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="发放人")
    approver_name = models.CharField(max_length=100, default="admin", verbose_name="批准人")
    issue_date = models.DateField(null=True, blank=True, verbose_name="发放日期")

    file_url = models.ImageField(
        upload_to='nvh_task/nvh_task_approval/',
        null=True, blank=True,
        verbose_name="文件(图片)"
    )

    status = models.CharField(max_length=20, default=STATUS_DRAFT, db_index=True, verbose_name="表单状态")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="提交时间")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "技术资料发放批准单"
        verbose_name_plural = "技术资料发放批准单"

    def __str__(self):
        return f"DocApproval(main_id={self.main_id})"
