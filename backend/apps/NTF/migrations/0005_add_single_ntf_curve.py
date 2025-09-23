from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NTF', '0004_drop_direction_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='ntftestresult',
            name='ntf_curve',
            field=models.JSONField(default=dict, blank=True, verbose_name='NTF原始数据'),
        ),
    ]

