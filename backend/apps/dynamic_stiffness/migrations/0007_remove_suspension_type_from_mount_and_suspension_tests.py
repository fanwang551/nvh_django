from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_stiffness', '0006_alter_dynamicstiffnessdata_freq_100_x_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehiclemountisolationtest',
            name='suspension_type',
        ),
        migrations.RemoveField(
            model_name='vehiclesuspensionisolationtest',
            name='suspension_type',
        ),
    ]

