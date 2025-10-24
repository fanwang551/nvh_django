# Generated manually for VOC_odor module upgrade

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voc', '0002_alter_vocresult_test_date'),
    ]

    operations = [
        # 重命名模型
        migrations.RenameModel(
            old_name='VocResult',
            new_name='VocOdorResult',
        ),
        
        # 修改表名
        migrations.AlterModelTable(
            name='vocodorresult',
            table='voc_odor_result',
        ),
        
        # 添加气味检测字段
        migrations.AddField(
            model_name='vocodorresult',
            name='static_front',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=6, null=True, verbose_name='静态-前排'),
        ),
        migrations.AddField(
            model_name='vocodorresult',
            name='static_rear',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=6, null=True, verbose_name='静态-后排'),
        ),
        migrations.AddField(
            model_name='vocodorresult',
            name='dynamic_front',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=6, null=True, verbose_name='动态-前排'),
        ),
        migrations.AddField(
            model_name='vocodorresult',
            name='dynamic_rear',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=6, null=True, verbose_name='动态-后排'),
        ),
        migrations.AddField(
            model_name='vocodorresult',
            name='odor_mean',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=6, null=True, verbose_name='气味均值'),
        ),
        
        # 添加 test_date 索引
        migrations.AddIndex(
            model_name='vocodorresult',
            index=models.Index(fields=['test_date'], name='voc_odor_re_test_da_b7a1e2_idx'),
        ),
        
        # 更新 Meta 配置
        migrations.AlterModelOptions(
            name='vocodorresult',
            options={'ordering': ['-id'], 'verbose_name': 'VOC和气味检测结果', 'verbose_name_plural': 'VOC和气味检测结果'},
        ),
    ]
