from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('NTF', '0004_alter_ntfinfo_location_alter_ntfinfo_test_time_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ntftestresult',
            unique_together=set(),
        ),
    ]

