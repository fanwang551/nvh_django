from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.modal.models import VehicleModel
from apps.NTF.models import NTFInfo, NTFTestResult


class NTFViewsTestCase(APITestCase):
    def setUp(self) -> None:
        self.vehicle = VehicleModel.objects.create(
            cle_model_code='SGMW-001',
            vehicle_model_name='测试车型A',
            vin='L1234567890123456',
            drive_type='FWD',
        )

    def _create_ntf_info(self, seat_count: int, offset_days: int = 0) -> NTFInfo:
        info = NTFInfo.objects.create(
            vehicle_model=self.vehicle,
            tester='张三',
            test_time=timezone.now() + timedelta(days=offset_days),
            location='NVH实验室',
            sunroof_type='全景天窗',
            suspension_type='麦弗逊',
            seat_count=seat_count,
            front_row_image='http://example.com/front.jpg',
            middle_row_image='http://example.com/middle.jpg',
            rear_row_image='http://example.com/rear.jpg',
            development_stage='SOP'
        )

        # Consolidated XYZ record for measurement point P1 (单曲线)
        NTFTestResult.objects.create(
            ntf_info=info,
            measurement_point='P1',
            x_target_value=60.0,
            x_front_row_value=61.0,
            x_middle_row_value=62.0,
            x_rear_row_value=63.5,
            y_target_value=60.0,
            y_front_row_value=61.0,
            y_middle_row_value=62.0,
            y_rear_row_value=63.5,
            ntf_curve={
                'frequency': [20, 40, 60],
                'values': [59.0, 61.0, 63.0],
            },
        )

        return info

    def test_ntf_detail_by_vehicle_returns_latest_record(self):
        self._create_ntf_info(seat_count=2, offset_days=-1)
        latest = self._create_ntf_info(seat_count=6, offset_days=0)

        url = f"/api/NTF/infos/by-vehicle/{self.vehicle.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.data.get('data')
        self.assertIsNotNone(payload)
        self.assertEqual(payload['seat_count'], latest.seat_count)

        seat_keys = [column['key'] for column in payload['seat_columns']]
        self.assertListEqual(seat_keys, ['front', 'middle', 'rear'])

        # 每条测试结果包含 X/Y/Z 三行（此处创建了一条，预期 3 行）
        self.assertEqual(len(payload['results']), latest.test_results.count() * 3)
        first_row = payload['results'][0]
        self.assertEqual(first_row['measurement_point'], 'P1')
        self.assertIn(first_row['direction'], {'X', 'Y', 'Z'})
        self.assertIn('front', first_row)
        self.assertEqual(payload['images']['front'], latest.front_row_image)

        heatmap = payload['heatmap']
        self.assertEqual(heatmap['frequency'], [20.0, 40.0, 60.0])
        self.assertEqual(heatmap['points'], ['P1'])
        # 单测点单曲线
        self.assertEqual(len(heatmap['matrix']), 1)

    def test_ntf_detail_handles_missing_vehicle(self):
        url = "/api/NTF/infos/by-vehicle/9999/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ntf_list_filters_by_vehicle(self):
        info = self._create_ntf_info(seat_count=5)

        url = reverse('ntf-info-list')
        response = self.client.get(url, {'vehicle_model': self.vehicle.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('data')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], info.id)
