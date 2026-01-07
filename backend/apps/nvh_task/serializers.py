from rest_framework import serializers
from .models import (
    MainRecord, EntryExit, TestInfo, DocApproval,
    TestProcessAttachment, TestProcessList
)


class EntryExitSerializer(serializers.ModelSerializer):
    """进出登记序列化器"""
    active_mainrecord_count = serializers.SerializerMethodField()

    class Meta:
        model = EntryExit
        fields = [
            'id', 'receiver_name', 'enter_time', 'purpose',
            'dispose_type', 'disposer_name', 'dispose_time', 'return_receiver',
            'remark', 'status', 'created_at', 'updated_at',
            'active_mainrecord_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'active_mainrecord_count']

    def get_active_mainrecord_count(self, obj):
        return obj.active_mainrecord_count()


class TestProcessAttachmentSerializer(serializers.ModelSerializer):
    """试验过程记录附件序列化器"""
    # 覆盖 file_url 字段，接受字符串路径
    file_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = TestProcessAttachment
        fields = ['id', 'test_info', 'record_name', 'file_url', 'sort_no', 'created_at']
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        """序列化时返回文件路径字符串"""
        ret = super().to_representation(instance)
        if instance.file_url:
            ret['file_url'] = instance.file_url.name if hasattr(instance.file_url, 'name') else str(instance.file_url)
        else:
            ret['file_url'] = ''
        return ret


class TestProcessListSerializer(serializers.ModelSerializer):
    """试验过程记录表清单序列化器"""

    class Meta:
        model = TestProcessList
        fields = ['id', 'test_process_name']
        read_only_fields = ['id']


class TestInfoSerializer(serializers.ModelSerializer):
    """试验信息序列化器"""
    process_attachments = TestProcessAttachmentSerializer(many=True, read_only=True)
    process_attachment_count = serializers.SerializerMethodField()
    # 覆盖 teardown_attachment_url 字段，接受字符串路径
    teardown_attachment_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = TestInfo
        fields = [
            'id', 'main', 'contact_phone', 'nvh_lab_mgmt_no',
            'sample_type', 'rd_stage', 'delivery_dept',
            'report_required', 'report_no',
            'include_teardown_record', 'include_process_record',
            'teardown_attachment_url',
            'status', 'submitted_at', 'created_at', 'updated_at',
            'process_attachments', 'process_attachment_count'
        ]
        read_only_fields = ['id', 'main', 'created_at', 'updated_at', 'process_attachments', 'process_attachment_count']

    def get_process_attachment_count(self, obj):
        return obj.process_attachments.count()

    def to_representation(self, instance):
        """序列化时返回文件路径字符串"""
        ret = super().to_representation(instance)
        # ImageField 转为字符串路径
        if instance.teardown_attachment_url:
            ret['teardown_attachment_url'] = instance.teardown_attachment_url.name if hasattr(instance.teardown_attachment_url, 'name') else str(instance.teardown_attachment_url)
        else:
            ret['teardown_attachment_url'] = ''
        return ret


class DocApprovalSerializer(serializers.ModelSerializer):
    """技术资料发放批准单序列化器"""
    # 覆盖 file_url 字段，接受字符串路径（已上传文件的相对路径）
    file_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = DocApproval
        fields = [
            'id', 'main', 'doc_name', 'doc_no', 'quantity',
            'receiver_name', 'issuer_name', 'approver_name', 'issue_date',
            'file_url', 'status', 'submitted_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'main', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """序列化时返回文件路径字符串"""
        ret = super().to_representation(instance)
        # ImageField 转为字符串路径
        if instance.file_url:
            ret['file_url'] = instance.file_url.name if hasattr(instance.file_url, 'name') else str(instance.file_url)
        else:
            ret['file_url'] = ''
        return ret


class MainRecordListSerializer(serializers.ModelSerializer):
    """主记录列表序列化器（含关联状态摘要）"""
    entry_exit_dispose_type = serializers.CharField(source='entry_exit.dispose_type', read_only=True)
    entry_exit_status = serializers.SerializerMethodField()
    test_info_status = serializers.SerializerMethodField()
    doc_approval_status = serializers.SerializerMethodField()
    include_teardown_record = serializers.SerializerMethodField()
    include_process_record = serializers.SerializerMethodField()

    class Meta:
        model = MainRecord
        fields = [
            'id', 'model', 'vin_or_part_no', 'test_name',
            'warning_system_status', 'requester_name',
            'schedule_start', 'schedule_end', 'schedule_remark', 'test_location',
            'tester_name', 'contract_no', 'remark',
            'entry_exit', 'entry_exit_dispose_type', 'is_closed', 'closure_checked_at',
            'created_at', 'updated_at',
            'entry_exit_status', 'test_info_status', 'doc_approval_status',
            'include_teardown_record', 'include_process_record'
        ]
        read_only_fields = ['id', 'is_closed', 'closure_checked_at', 'created_at', 'updated_at']

    def get_entry_exit_status(self, obj):
        if obj.entry_exit and not obj.entry_exit.is_deleted:
            return obj.entry_exit.status
        return None

    def get_test_info_status(self, obj):
        try:
            if obj.test_info and not obj.test_info.is_deleted:
                return obj.test_info.status
        except TestInfo.DoesNotExist:
            pass
        return None

    def get_doc_approval_status(self, obj):
        try:
            if obj.doc_approval and not obj.doc_approval.is_deleted:
                return obj.doc_approval.status
        except DocApproval.DoesNotExist:
            pass
        return None

    def get_include_teardown_record(self, obj):
        try:
            if obj.test_info and not obj.test_info.is_deleted:
                return obj.test_info.include_teardown_record
        except TestInfo.DoesNotExist:
            pass
        return None

    def get_include_process_record(self, obj):
        try:
            if obj.test_info and not obj.test_info.is_deleted:
                return obj.test_info.include_process_record
        except TestInfo.DoesNotExist:
            pass
        return None


class MainRecordDetailSerializer(serializers.ModelSerializer):
    """主记录详情序列化器（含完整关联数据）"""
    entry_exit = EntryExitSerializer(read_only=True)
    test_info = TestInfoSerializer(read_only=True)
    doc_approval = DocApprovalSerializer(read_only=True)

    class Meta:
        model = MainRecord
        fields = [
            'id', 'model', 'vin_or_part_no', 'test_name',
            'warning_system_status', 'requester_name',
            'schedule_start', 'schedule_end', 'schedule_remark', 'test_location',
            'tester_name', 'contract_no', 'remark',
            'entry_exit', 'is_closed', 'closure_checked_at',
            'created_at', 'updated_at',
            'test_info', 'doc_approval'
        ]
        read_only_fields = ['id', 'is_closed', 'closure_checked_at', 'created_at', 'updated_at']


class MainRecordCreateUpdateSerializer(serializers.ModelSerializer):
    """主记录创建/更新序列化器"""
    entry_exit_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = MainRecord
        fields = [
            'id', 'model', 'vin_or_part_no', 'test_name',
            'warning_system_status', 'requester_name',
            'schedule_start', 'schedule_end', 'schedule_remark', 'test_location',
            'tester_name', 'contract_no', 'remark',
            'entry_exit_id'
        ]
        read_only_fields = ['id']

    def validate_entry_exit_id(self, value):
        if value is not None:
            if not EntryExit.objects.filter(id=value).exists():
                raise serializers.ValidationError("关联的进出登记不存在")
        return value

    def create(self, validated_data):
        entry_exit_id = validated_data.pop('entry_exit_id', None)
        if entry_exit_id:
            validated_data['entry_exit_id'] = entry_exit_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        entry_exit_id = validated_data.pop('entry_exit_id', None)
        if 'entry_exit_id' in self.initial_data:
            # 显式传入了 entry_exit_id（包括 null）
            instance.entry_exit_id = entry_exit_id
        return super().update(instance, validated_data)
