from django.db import migrations, models
import django.db.models.deletion


def forwards_fill_condition_point(apps, schema_editor):
    # Historical models
    TDA = apps.get_model('acoustic_analysis', 'TestDataAll')
    CMP = apps.get_model('acoustic_analysis', 'ConditionMeasurePoint')

    # Create or get ConditionMeasurePoint for each distinct pair, then update rows
    # Build mapping cache to reduce queries
    pairs = (
        TDA.objects
        .values_list('work_condition', 'measure_point')
        .distinct()
    )
    pair_to_id = {}
    for wc, mp in pairs:
        obj, _ = CMP.objects.get_or_create(work_condition=wc, measure_point=mp)
        pair_to_id[(wc, mp)] = obj.id

    # Bulk updates per pair
    for (wc, mp), cmp_id in pair_to_id.items():
        TDA.objects.filter(work_condition=wc, measure_point=mp).update(condition_point_id=cmp_id)


def backwards_unfill_condition_point(apps, schema_editor):
    # Best-effort: restore work_condition/measure_point from related CMP
    # Note: at this point fields may have been removed already in later operations; this is for completeness
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('acoustic_analysis', '0001_initial'),
    ]

    operations = [
        # 1) Create dimension table
        migrations.CreateModel(
            name='ConditionMeasurePoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_condition', models.CharField(db_index=True, max_length=100, verbose_name='工况')),
                ('measure_point', models.CharField(db_index=True, max_length=100, verbose_name='测点')),
            ],
            options={
                'verbose_name': '工况测点',
                'verbose_name_plural': '工况测点',
                'db_table': 'condition_measure_point',
                'ordering': ['work_condition', 'measure_point'],
                'indexes': [
                    models.Index(fields=['work_condition', 'measure_point'], name='idx_cm_wc_mp'),
                ],
            },
        ),

        # 2) Add nullable FK to existing table
        migrations.AddField(
            model_name='testdataall',
            name='condition_point',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='test_data', to='acoustic_analysis.conditionmeasurepoint', verbose_name='工况测点'),
        ),

        # 3) Remove old composite index before dropping columns
        migrations.RemoveIndex(
            model_name='testdataall',
            name='idx_vm_wc_mp',
        ),

        # 4) Data migration to populate FK
        migrations.RunPython(forwards_fill_condition_point, backwards_unfill_condition_point),

        # 5) Make FK non-nullable
        migrations.AlterField(
            model_name='testdataall',
            name='condition_point',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='test_data', to='acoustic_analysis.conditionmeasurepoint', verbose_name='工况测点'),
        ),

        # 6) Drop legacy columns
        migrations.RemoveField(
            model_name='testdataall',
            name='work_condition',
        ),
        migrations.RemoveField(
            model_name='testdataall',
            name='measure_point',
        ),
        migrations.RemoveField(
            model_name='testdataall',
            name='created_at',
        ),

        # 7) Add new composite index (vehicle_model, condition_point)
        migrations.AddIndex(
            model_name='testdataall',
            index=models.Index(fields=['vehicle_model', 'condition_point'], name='idx_vm_cp'),
        ),

        # 8) Update model options (ordering)
        migrations.AlterModelOptions(
            name='testdataall',
            options={
                'verbose_name': '声学测试数据',
                'verbose_name_plural': '声学测试数据',
                'ordering': [
                    'vehicle_model_id',
                    'condition_point__work_condition',
                    'condition_point__measure_point',
                    '-test_date',
                    '-id',
                ],
            },
        ),

        # 9) Rename model to AcousticTestData (DB table unchanged)
        migrations.RenameModel(
            old_name='TestDataAll',
            new_name='AcousticTestData',
        ),
    ]
