from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acoustic_analysis', '0002_split_condition_measure_point'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='acoustictestdata',
            index=models.Index(
                fields=['vehicle_model', 'condition_point', 'test_date', 'id'],
                name='idx_vm_cp_date_id',
            ),
        ),
    ]

