from django.db import migrations


def choose_curve(data):
    if not isinstance(data, dict):
        return None
    values = data.get('values')
    if isinstance(values, (list, tuple)) and len(values) > 0:
        return data
    return None


def forward(apps, schema_editor):
    TestResult = apps.get_model('NTF', 'NTFTestResult')
    for row in TestResult.objects.all().only('id', 'ntf_curve'):
        # These attributes may not exist if removed, so use getattr safely
        x_curve = getattr(row, 'x_ntf_curve', None)
        y_curve = getattr(row, 'y_ntf_curve', None)
        z_curve = getattr(row, 'z_ntf_curve', None)

        selected = choose_curve(x_curve) or choose_curve(y_curve) or choose_curve(z_curve)
        if selected:
            row.ntf_curve = selected
            row.save(update_fields=['ntf_curve'])


class Migration(migrations.Migration):

    dependencies = [
        ('NTF', '0005_add_single_ntf_curve'),
    ]

    operations = [
        migrations.RunPython(forward, migrations.RunPython.noop),
    ]

