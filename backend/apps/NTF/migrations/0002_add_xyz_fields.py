from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NTF', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ntftestresult',
            name='x_target_value',
            field=models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, verbose_name='X方向目标(dB)'),
        ),
        migrations.AddField(
            model_name='ntftestresult',
            name='x_front_row_value',
            field=models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, verbose_name='X方向前排(dB)'),
        ),
        migrations.AddField(
            model_name='ntftestresult',
            name='x_middle_row_value',
            field=models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, verbose_name='X方向中排(dB)'),
        ),
        migrations.AddField(
            model_name='ntftestresult',
            name='x_rear_row_value',
            field=models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, verbose_name='X方向后排(dB)'),
        ),
        migrations.AddField(
            model_name='ntftestresult',
            name='x_ntf_curve',
            field=models.JSONField(default=dict, blank=True, verbose_name='X方向NTF原始数据'),
        ),

        migrations.AddField(
            model_name='ntftestresult',
            name='y_target_value',
            field=models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, verbose_name='Y方向目标(dB)'),
        ),
        migrations.AddField(
            model_name='ntftestresult',
            name='y_front_row_value',
            field=models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, verbose_name='Y方向前排(dB)'),
        ),
        migrations.AddField(
            model_name='ntftestresult',
            name='y_middle_row_value',
            field=models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, verbose_name='Y方向中排(dB)'),
        ),
        migrations.AddField(
            model_name='ntftestresult',
            name='y_rear_row_value',
            field=models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, verbose_name='Y方向后排(dB)'),
        ),
        migrations.AddField(
            model_name='ntftestresult',
            name='y_ntf_curve',
            field=models.JSONField(default=dict, blank=True, verbose_name='Y方向NTF原始数据'),
        ),

        migrations.AddField(
            model_name='ntftestresult',
            name='z_target_value',
            field=models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, verbose_name='Z方向目标(dB)'),
        ),
        migrations.AddField(
            model_name='ntftestresult',
            name='z_front_row_value',
            field=models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, verbose_name='Z方向前排(dB)'),
        ),
        migrations.AddField(
            model_name='ntftestresult',
            name='z_middle_row_value',
            field=models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, verbose_name='Z方向中排(dB)'),
        ),
        migrations.AddField(
            model_name='ntftestresult',
            name='z_rear_row_value',
            field=models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, verbose_name='Z方向后排(dB)'),
        ),
        migrations.AddField(
            model_name='ntftestresult',
            name='z_ntf_curve',
            field=models.JSONField(default=dict, blank=True, verbose_name='Z方向NTF原始数据'),
        ),
    ]

