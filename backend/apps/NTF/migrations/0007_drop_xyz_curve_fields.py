from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('NTF', '0006_migrate_xyz_curve_to_single'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ntftestresult',
            name='x_ntf_curve',
        ),
        migrations.RemoveField(
            model_name='ntftestresult',
            name='y_ntf_curve',
        ),
        migrations.RemoveField(
            model_name='ntftestresult',
            name='z_ntf_curve',
        ),
    ]

