from django.db import models


def default_media():
    return {"images": [], "videos": []}


class Experience(models.Model):
    """经验数据库表"""

    # 使用 INT 主键，覆盖项目默认的 BigAutoField
    id = models.AutoField(primary_key=True)

    # 基本信息
    category = models.CharField(max_length=100, verbose_name='问题分类')
    problem_name = models.CharField(max_length=200, verbose_name='问题名称')
    keywords = models.CharField(max_length=500, verbose_name='问题关键字（多个关键字用逗号分隔）')
    description = models.TextField(verbose_name='问题描述')

    # 媒体信息（JSON 格式）
    problem_media = models.JSONField(null=True, blank=True, default=default_media, verbose_name='问题描述图片及视频')
    analysis_content = models.TextField(null=True, blank=True, verbose_name='问题分析内容')
    analysis_media = models.JSONField(null=True, blank=True, default=default_media, verbose_name='问题分析图片及视频')
    solution_content = models.TextField(null=True, blank=True, verbose_name='解决方案与措施')
    solution_media = models.JSONField(null=True, blank=True, default=default_media, verbose_name='解决方案与措施图片及视频')

    # 审计信息
    creator = models.CharField(max_length=100, null=True, blank=True, verbose_name='创建人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'experience'
        verbose_name = '经验'
        verbose_name_plural = '经验'
        ordering = ['-create_time', '-id']

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.problem_name}"

