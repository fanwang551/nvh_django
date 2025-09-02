from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from utils.response import Response
from .models import SoundInsulationArea, SoundInsulationData, VehicleSoundInsulationData, VehicleReverberationData
from .serializers import (
    SoundInsulationAreaSerializer, SoundInsulationDataSerializer,
    SoundInsulationCompareSerializer, VehicleModelSimpleSerializer,
    VehicleSoundInsulationDataSerializer, VehicleSoundInsulationCompareSerializer,
    VehicleReverberationDataSerializer, VehicleReverberationCompareSerializer
)
from apps.modal.models import VehicleModel


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def sound_insulation_area_list(request):
    """获取隔声区域列表"""
    try:
        queryset = SoundInsulationArea.objects.all().order_by('id')

        # 支持按区域名称搜索
        search = request.GET.get('search', '')
        if search:
            queryset = queryset.filter(area_name__icontains=search)

        serializer = SoundInsulationAreaSerializer(queryset, many=True)
        return Response.success(data=serializer.data, message="获取区域列表成功")

    except Exception as e:
        return Response.error(message=f"获取区域列表失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_vehicles_by_area(request):
    """根据区域ID获取有数据的车型列表"""
    try:
        area_id = request.GET.get('area_id')
        if not area_id:
            return Response.error(message="区域ID不能为空", status_code=status.HTTP_400_BAD_REQUEST)

        # 验证区域是否存在
        if not SoundInsulationArea.objects.filter(id=area_id).exists():
            return Response.error(message="指定的区域不存在", status_code=status.HTTP_400_BAD_REQUEST)

        # 获取该区域有数据的车型
        vehicle_models = VehicleModel.objects.filter(
            soundinsulationdata__area_id=area_id,
            status='active'
        ).distinct().order_by('id')

        serializer = VehicleModelSimpleSerializer(vehicle_models, many=True)
        return Response.success(data=serializer.data, message="获取车型列表成功")

    except Exception as e:
        return Response.error(message=f"获取车型列表失败: {str(e)}")


@api_view(['POST'])
@permission_classes([])  # 临时允许匿名访问用于测试
def sound_insulation_compare(request):
    """隔声量数据对比"""
    try:
        serializer = SoundInsulationCompareSerializer(data=request.data)
        if not serializer.is_valid():
            return Response.error(
                message="参数验证失败",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        area_id = serializer.validated_data['area_id']
        vehicle_model_ids_str = serializer.validated_data['vehicle_model_ids']

        # 解析车型ID列表
        vehicle_model_ids = [int(id.strip()) for id in vehicle_model_ids_str.split(',') if id.strip()]

        # 查询隔声量数据
        queryset = SoundInsulationData.objects.select_related(
            'vehicle_model', 'area'
        ).filter(
            area_id=area_id,
            vehicle_model_id__in=vehicle_model_ids
        ).order_by('vehicle_model__id')

        if not queryset.exists():
            return Response.success(data=[], message="未找到匹配的隔声量数据")

        # 构建对比数据
        compare_data = []
        frequency_fields = [
            'freq_200', 'freq_250', 'freq_315', 'freq_400', 'freq_500', 'freq_630',
            'freq_800', 'freq_1000', 'freq_1250', 'freq_1600', 'freq_2000', 'freq_2500',
            'freq_3150', 'freq_4000', 'freq_5000', 'freq_6300', 'freq_8000', 'freq_10000'
        ]

        for data in queryset:
            # 构建频率数据字典
            frequency_data = {}
            for field in frequency_fields:
                value = getattr(data, field)
                frequency_data[field] = float(value) if value is not None else None

            compare_data.append({
                'id': data.id,
                'vehicle_model_id': data.vehicle_model.id,
                'vehicle_model_name': data.vehicle_model.vehicle_model_name,
                'area_id': data.area.id,
                'area_name': data.area.area_name,
                'frequency_data': frequency_data,
                'test_image_path': data.test_image_path,
                'test_date': data.test_date.isoformat() if data.test_date else None,
                'test_location': data.test_location,
                'test_engineer': data.test_engineer,
                'remarks': data.remarks
            })

        return Response.success(data=compare_data, message="对比数据获取成功")

    except Exception as e:
        return Response.error(message=f"获取对比数据失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_vehicles_with_sound_data(request):
    """获取有车型隔声量数据的车型列表"""
    try:
        # 获取有隔声量数据的车型
        vehicle_models = VehicleModel.objects.filter(
            vehiclesoundinsulationdata__isnull=False,
            status='active'
        ).distinct().order_by('id')

        serializer = VehicleModelSimpleSerializer(vehicle_models, many=True)
        return Response.success(data=serializer.data, message="获取车型列表成功")

    except Exception as e:
        return Response.error(message=f"获取车型列表失败: {str(e)}")


@api_view(['POST'])
@permission_classes([])  # 临时允许匿名访问用于测试
def vehicle_sound_insulation_compare(request):
    """车型隔声量数据对比"""
    try:
        serializer = VehicleSoundInsulationCompareSerializer(data=request.data)
        if not serializer.is_valid():
            return Response.error(
                message="参数验证失败",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        vehicle_model_ids_str = serializer.validated_data['vehicle_model_ids']

        # 解析车型ID列表
        vehicle_model_ids = [int(id.strip()) for id in vehicle_model_ids_str.split(',') if id.strip()]

        # 查询车型隔声量数据
        queryset = VehicleSoundInsulationData.objects.select_related(
            'vehicle_model'
        ).filter(
            vehicle_model_id__in=vehicle_model_ids
        ).order_by('vehicle_model__id')

        if not queryset.exists():
            return Response.success(data=[], message="未找到匹配的车型隔声量数据")

        # 构建对比数据
        compare_data = []
        frequency_fields = [
            'freq_200', 'freq_250', 'freq_315', 'freq_400', 'freq_500', 'freq_630',
            'freq_800', 'freq_1000', 'freq_1250', 'freq_1600', 'freq_2000', 'freq_2500',
            'freq_3150', 'freq_4000', 'freq_5000', 'freq_6300', 'freq_8000', 'freq_10000'
        ]

        for data in queryset:
            # 构建频率数据字典
            frequency_data = {}
            for field in frequency_fields:
                value = getattr(data, field)
                frequency_data[field] = float(value) if value is not None else None

            compare_data.append({
                'id': data.id,
                'vehicle_model_id': data.vehicle_model.id,
                'vehicle_model_name': data.vehicle_model.vehicle_model_name,
                'vehicle_model_code': data.vehicle_model.cle_model_code,
                'frequency_data': frequency_data,
                'test_image_path': data.test_image_path,
                'test_date': data.test_date.isoformat() if data.test_date else None,
                'test_location': data.test_location,
                'test_engineer': data.test_engineer,
                'remarks': data.remarks
            })

        return Response.success(data=compare_data, message="车型隔声量对比数据获取成功")

    except Exception as e:
        return Response.error(message=f"获取对比数据失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_vehicles_with_reverberation_data(request):
    """获取有车辆混响时间数据的车型列表"""
    try:
        # 获取有混响时间数据的车型
        vehicle_models = VehicleModel.objects.filter(
            vehiclereverberationdata__isnull=False,
            status='active'
        ).distinct().order_by('id')

        serializer = VehicleModelSimpleSerializer(vehicle_models, many=True)
        return Response.success(data=serializer.data, message="获取车型列表成功")

    except Exception as e:
        return Response.error(message=f"获取车型列表失败: {str(e)}")


@api_view(['POST'])
@permission_classes([])  # 临时允许匿名访问用于测试
def vehicle_reverberation_compare(request):
    """车辆混响时间数据对比"""
    try:
        serializer = VehicleReverberationCompareSerializer(data=request.data)
        if not serializer.is_valid():
            return Response.error(
                message="参数验证失败",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        vehicle_model_ids_str = serializer.validated_data['vehicle_model_ids']

        # 解析车型ID列表
        vehicle_model_ids = [int(id.strip()) for id in vehicle_model_ids_str.split(',') if id.strip()]

        # 查询车辆混响时间数据
        queryset = VehicleReverberationData.objects.select_related(
            'vehicle_model'
        ).filter(
            vehicle_model_id__in=vehicle_model_ids
        ).order_by('vehicle_model__id')

        if not queryset.exists():
            return Response.success(data=[], message="未找到匹配的车辆混响时间数据")

        # 构建对比数据
        compare_data = []
        frequency_fields = [
            'freq_400', 'freq_500', 'freq_630', 'freq_800', 'freq_1000', 'freq_1250',
            'freq_1600', 'freq_2000', 'freq_2500', 'freq_3150', 'freq_4000', 'freq_5000',
            'freq_6300', 'freq_8000', 'freq_10000'
        ]

        for data in queryset:
            # 构建频率数据字典
            frequency_data = {}
            for field in frequency_fields:
                value = getattr(data, field)
                frequency_data[field] = float(value) if value is not None else None

            compare_data.append({
                'id': data.id,
                'vehicle_model_id': data.vehicle_model.id,
                'vehicle_model_name': data.vehicle_model.vehicle_model_name,
                'vehicle_model_code': data.vehicle_model.cle_model_code,
                'frequency_data': frequency_data,
                'test_image_path': data.test_image_path,
                'test_date': data.test_date.isoformat() if data.test_date else None,
                'test_location': data.test_location,
                'test_engineer': data.test_engineer,
                'remarks': data.remarks
            })

        return Response.success(data=compare_data, message="车辆混响时间对比数据获取成功")

    except Exception as e:
        return Response.error(message=f"获取车辆混响时间对比数据失败: {str(e)}")
