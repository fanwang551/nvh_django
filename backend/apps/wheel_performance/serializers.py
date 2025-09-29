from rest_framework import serializers

from apps.wheel_performance.models import WheelPerformance


class WheelPerformanceSerializer(serializers.ModelSerializer):
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)

    class Meta:
        model = WheelPerformance
        fields = (
            'id',
            'vehicle_model',
            'vehicle_model_name',
            'tire_brand',
            'tire_model',
            'is_silent',
            'rim_material',
            'rim_mass_mt',
            'resonance_peak_f1',
            'anti_resonance_peak_f2',
            'rim_lateral_stiffness',
            'rim_stiffness_curve_url',
            'rim_stiffness_test_image_url',
            'force_transfer_first_peak',
            'force_transfer_test_image_url',
            'force_transfer_signal',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        signal = data.get('force_transfer_signal')

        # 仅在是 dict 且包含 frequency / dB 时尝试修正
        try:
            parsed = signal
            if isinstance(parsed, str):
                import json
                parsed = json.loads(parsed)
            if isinstance(parsed, dict):
                freq_raw = parsed.get('frequency')
                db_raw = parsed.get('dB') if 'dB' in parsed else parsed.get('db')
                if isinstance(freq_raw, list) and isinstance(db_raw, list):
                    n_freq = [float(x) for x in freq_raw if isinstance(x, (int, float, str)) and str(x).strip() not in ('', 'nan')]
                    n_db = [float(x) for x in db_raw if isinstance(x, (int, float, str)) and str(x).strip() not in ('', 'nan')]

                    def stats(arr):
                        if not arr:
                            return (float('inf'), float('-inf'), float('nan'))
                        mn, mx = min(arr), max(arr)
                        return (mn, mx, mx - mn)

                    f_min, f_max, f_rng = stats(n_freq)
                    d_min, d_max, d_rng = stats(n_db)

                    looks_like_freq = (f_max >= 80) and (f_max <= 5000)
                    looks_like_db = (d_rng <= 160) and (d_max <= 160) and (d_min >= -160)
                    freq_looks_db = (f_rng <= 160) and (f_max <= 160) and (f_min >= -160)
                    db_looks_freq = (d_max >= 80)

                    # 判断是否对调
                    if not looks_like_freq and not looks_like_db and freq_looks_db and db_looks_freq:
                        n_freq, n_db = n_db, n_freq

                    # 输出为标准结构
                    # 保留原始顺序，不进行重采样/排序
                    data['force_transfer_signal'] = {
                        'frequency': n_freq,
                        'dB': n_db,
                    }
        except Exception:
            # 容错：若出错则原样返回
            pass

        return data


class WheelPerformanceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WheelPerformance
        fields = (
            'vehicle_model',
            'tire_brand',
            'tire_model',
            'is_silent',
            'rim_material',
            'rim_mass_mt',
            'resonance_peak_f1',
            'anti_resonance_peak_f2',
            'rim_lateral_stiffness',
            'rim_stiffness_curve_url',
            'rim_stiffness_test_image_url',
            'force_transfer_first_peak',
            'force_transfer_test_image_url',
            'force_transfer_signal',
        )
