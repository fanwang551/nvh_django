from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('NTF', '0008_ntftestresult_layout_image_url_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ntfinfo',
            name='front_row_image',
        ),
        migrations.RemoveField(
            model_name='ntfinfo',
            name='middle_row_image',
        ),
        migrations.RemoveField(
            model_name='ntfinfo',
            name='rear_row_image',
        ),
    ]

