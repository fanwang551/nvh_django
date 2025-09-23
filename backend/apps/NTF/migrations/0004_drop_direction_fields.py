from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('NTF', '0003_consolidate_direction_rows'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ntftestresult',
            options={
                'verbose_name': 'NTF测试结果',
                'verbose_name_plural': 'NTF测试结果',
                'db_table': 'NTF_test_result',
                'ordering': ['measurement_point'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='ntftestresult',
            unique_together={('ntf_info', 'measurement_point')},
        ),
        migrations.RemoveField(
            model_name='ntftestresult',
            name='direction',
        ),
        migrations.RemoveField(
            model_name='ntftestresult',
            name='target_value',
        ),
        migrations.RemoveField(
            model_name='ntftestresult',
            name='front_row_value',
        ),
        migrations.RemoveField(
            model_name='ntftestresult',
            name='middle_row_value',
        ),
        migrations.RemoveField(
            model_name='ntftestresult',
            name='rear_row_value',
        ),
        migrations.RemoveField(
            model_name='ntftestresult',
            name='ntf_curve',
        ),
    ]

