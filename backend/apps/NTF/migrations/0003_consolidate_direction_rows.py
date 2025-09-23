from django.db import migrations


def consolidate_rows(apps, schema_editor):
    TestResult = apps.get_model('NTF', 'NTFTestResult')

    # Group existing rows by (ntf_info_id, measurement_point)
    from collections import defaultdict

    groups = defaultdict(list)
    for row in TestResult.objects.all().only(
        'id', 'ntf_info_id', 'measurement_point', 'direction',
        'target_value', 'front_row_value', 'middle_row_value', 'rear_row_value', 'ntf_curve',
    ):
        key = (row.ntf_info_id, row.measurement_point)
        groups[key].append(row)

    for (ntf_info_id, point), rows in groups.items():
        # Pick master row: prefer X, else Y, else Z, else first
        order = {'X': 0, 'Y': 1, 'Z': 2}
        master = sorted(rows, key=lambda r: order.get(getattr(r, 'direction', ''), 9))[0]

        # Fill X/Y/Z fields on master
        for r in rows:
            dir_code = getattr(r, 'direction', None)
            if dir_code not in {'X', 'Y', 'Z'}:
                continue
            prefix = dir_code.lower()
            setattr(master, f"{prefix}_target_value", r.target_value)
            setattr(master, f"{prefix}_front_row_value", r.front_row_value)
            setattr(master, f"{prefix}_middle_row_value", r.middle_row_value)
            setattr(master, f"{prefix}_rear_row_value", r.rear_row_value)
            setattr(master, f"{prefix}_ntf_curve", r.ntf_curve or {})

        master.save(update_fields=[
            'x_target_value', 'x_front_row_value', 'x_middle_row_value', 'x_rear_row_value', 'x_ntf_curve',
            'y_target_value', 'y_front_row_value', 'y_middle_row_value', 'y_rear_row_value', 'y_ntf_curve',
            'z_target_value', 'z_front_row_value', 'z_middle_row_value', 'z_rear_row_value', 'z_ntf_curve',
        ])

        # Delete non-master rows
        for r in rows:
            if r.id != master.id:
                r.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('NTF', '0002_add_xyz_fields'),
    ]

    operations = [
        migrations.RunPython(consolidate_rows, migrations.RunPython.noop),
    ]

