from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from utils.response import Response
from .models import (
    SoundInsulationArea, SoundInsulationData, VehicleSoundInsulationData,
    VehicleReverberationData, SoundAbsorptionCoefficients, SoundInsulationCoefficients,
    MaterialPorosityFlowResistance
)
from .serializers import (
    SoundInsulationAreaSerializer, SoundInsulationDataSerializer,
    SoundInsulationCompareSerializer, VehicleModelSimpleSerializer,
    VehicleSoundInsulationDataSerializer, VehicleSoundInsulationCompareSerializer,
    VehicleReverberationDataSerializer, VehicleReverberationCompareSerializer,
    SoundAbsorptionCoefficientsSerializer, SoundAbsorptionQuerySerializer,
    PartNameOptionSerializer, MaterialCompositionOptionSerializer, WeightOptionSerializer,
    SoundInsulationCoefficientsSerializer, SoundInsulationCoefficientQuerySerializer,
    TestTypeOptionSerializer, InsulationPartNameOptionSerializer,
    InsulationMaterialCompositionOptionSerializer, InsulationWeightOptionSerializer,
    MaterialPorosityFlowResistanceSerializer, MaterialPorosityQuerySerializer,
    MaterialPorosityPartNameOptionSerializer
)
from apps.modal.models import VehicleModel
import json


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


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def sound_insulation_compare(request):
    """隔声量数据对比"""
    try:
        # 获取查询参数
        area_id = request.GET.get('area_id')
        vehicle_model_ids_str = request.GET.get('vehicle_model_ids')

        # 参数验证
        if not area_id:
            return Response.error(message="区域ID不能为空", status_code=status.HTTP_400_BAD_REQUEST)

        if not vehicle_model_ids_str:
            return Response.error(message="车型ID列表不能为空", status_code=status.HTTP_400_BAD_REQUEST)

        try:
            area_id = int(area_id)
        except ValueError:
            return Response.error(message="区域ID格式错误", status_code=status.HTTP_400_BAD_REQUEST)

        # 解析车型ID列表
        try:
            vehicle_model_ids = [int(id.strip()) for id in vehicle_model_ids_str.split(',') if id.strip()]
            if not vehicle_model_ids:
                return Response.error(message="车型ID列表不能为空", status_code=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response.error(message="车型ID格式错误，请使用逗号分隔的数字", status_code=status.HTTP_400_BAD_REQUEST)

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
                'test_image_path': (data.test_image_path or []),
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


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def vehicle_sound_insulation_compare(request):
    """车型隔声量数据对比"""
    try:
        # 获取查询参数
        vehicle_model_ids_str = request.GET.get('vehicle_model_ids')

        # 参数验证
        if not vehicle_model_ids_str:
            return Response.error(message="车型ID列表不能为空", status_code=status.HTTP_400_BAD_REQUEST)

        # 解析车型ID列表
        try:
            vehicle_model_ids = [int(id.strip()) for id in vehicle_model_ids_str.split(',') if id.strip()]
            if not vehicle_model_ids:
                return Response.error(message="车型ID列表不能为空", status_code=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response.error(message="车型ID格式错误，请使用逗号分隔的数字", status_code=status.HTTP_400_BAD_REQUEST)

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
                'test_image_path': (data.test_image_path or []),
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


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def vehicle_reverberation_compare(request):
    """车辆混响时间数据对比"""
    try:
        # 获取查询参数
        vehicle_model_ids_str = request.GET.get('vehicle_model_ids')

        # 参数验证
        if not vehicle_model_ids_str:
            return Response.error(message="车型ID列表不能为空", status_code=status.HTTP_400_BAD_REQUEST)

        # 解析车型ID列表
        try:
            vehicle_model_ids = [int(id.strip()) for id in vehicle_model_ids_str.split(',') if id.strip()]
            if not vehicle_model_ids:
                return Response.error(message="车型ID列表不能为空", status_code=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response.error(message="车型ID格式错误，请使用逗号分隔的数字", status_code=status.HTTP_400_BAD_REQUEST)

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

        def _parse_image_paths(value):
            """规范图片路径字段为数组，兼容 JSON 字符串。"""
            if value is None:
                return []
            if isinstance(value, list):
                return [v for v in value if v]
            if isinstance(value, str):
                s = value.strip()
                if not s:
                    return []
                if s.startswith('[') and s.endswith(']'):
                    try:
                        arr = json.loads(s)
                        if isinstance(arr, list):
                            return [v for v in arr if v]
                    except Exception:
                        pass
                return [s]
            return []

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
                'test_image_path': _parse_image_paths(data.test_image_path),
                'test_date': data.test_date.isoformat() if data.test_date else None,
                'test_location': data.test_location,
                'test_engineer': data.test_engineer,
                'remarks': data.remarks
            })

        return Response.success(data=compare_data, message="车辆混响时间对比数据获取成功")

    except Exception as e:
        return Response.error(message=f"获取车辆混响时间对比数据失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_part_name_options(request):
    """获取零件名称选项列表"""
    try:
        # 获取所有不重复的零件名称
        part_names = SoundAbsorptionCoefficients.objects.values_list('part_name', flat=True).distinct().order_by('part_name')
        
        options = []
        for part_name in part_names:
            options.append({
                'value': part_name,
                'label': part_name  # 直接使用实际名称
            })
        
        serializer = PartNameOptionSerializer(options, many=True)
        return Response.success(data=serializer.data, message="获取零件名称选项成功")
    
    except Exception as e:
        return Response.error(message=f"获取零件名称选项失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_material_composition_options(request):
    """根据零件名称获取材料组成选项列表"""
    try:
        part_name = request.GET.get('part_name')
        
        queryset = SoundAbsorptionCoefficients.objects.all()
        if part_name:
            queryset = queryset.filter(part_name=part_name)
        
        # 获取所有不重复的材料组成
        material_compositions = queryset.values_list('material_composition', 'part_name').distinct().order_by('material_composition')
        
        options = []
        for material_composition, related_part_name in material_compositions:
            options.append({
                'value': material_composition,
                'label': material_composition,  # 直接使用实际名称
                'part_name': related_part_name
            })
        
        serializer = MaterialCompositionOptionSerializer(options, many=True)
        return Response.success(data=serializer.data, message="获取材料组成选项成功")
    
    except Exception as e:
        return Response.error(message=f"获取材料组成选项失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_weight_options(request):
    """根据零件名称和材料组成获取克重选项列表"""
    try:
        part_name = request.GET.get('part_name')
        material_composition = request.GET.get('material_composition')
        
        queryset = SoundAbsorptionCoefficients.objects.all()
        if part_name:
            queryset = queryset.filter(part_name=part_name)
        if material_composition:
            queryset = queryset.filter(material_composition=material_composition)
        
        # 获取所有不重复的克重
        weights = queryset.values_list('weight', 'part_name', 'material_composition').distinct().order_by('weight')
        
        options = []
        for weight, related_part_name, related_material_composition in weights:
            options.append({
                'value': weight,
                'label': f'{weight}g/m²',
                'part_name': related_part_name,
                'material_composition': related_material_composition
            })
        
        serializer = WeightOptionSerializer(options, many=True)
        return Response.success(data=serializer.data, message="获取克重选项成功")
    
    except Exception as e:
        return Response.error(message=f"获取克重选项失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def sound_absorption_query(request):
    """吸声系数查询"""
    try:
        # 获取查询参数
        part_name = request.GET.get('part_name')
        material_composition = request.GET.get('material_composition')
        weight = request.GET.get('weight')

        # 参数验证 - 至少需要一个查询条件
        if not any([part_name, material_composition, weight]):
            return Response.error(
                message="至少需要提供一个查询条件",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # 构建查询条件
        filters = {}
        if part_name:
            filters['part_name'] = part_name
        if material_composition:
            filters['material_composition'] = material_composition
        if weight:
            try:
                filters['weight'] = float(weight)
            except ValueError:
                return Response.error(message="克重格式错误", status_code=status.HTTP_400_BAD_REQUEST)
        
        # 查询吸声系数数据
        queryset = SoundAbsorptionCoefficients.objects.filter(**filters).order_by('-id')
        
        if not queryset.exists():
            return Response.success(data=[], message="未找到匹配的吸声系数数据")
        
        # 构建查询结果
        query_data = []
        frequency_fields = [
            'test_value_125', 'test_value_160', 'test_value_200', 'test_value_250',
            'test_value_315', 'test_value_400', 'test_value_500', 'test_value_630',
            'test_value_800', 'test_value_1000', 'test_value_1250', 'test_value_1600',
            'test_value_2000', 'test_value_2500', 'test_value_3150', 'test_value_4000',
            'test_value_5000', 'test_value_6300', 'test_value_8000', 'test_value_10000'
        ]
        
        target_fields = [
            'target_value_125', 'target_value_160', 'target_value_200', 'target_value_250',
            'target_value_315', 'target_value_400', 'target_value_500', 'target_value_630',
            'target_value_800', 'target_value_1000', 'target_value_1250', 'target_value_1600',
            'target_value_2000', 'target_value_2500', 'target_value_3150', 'target_value_4000',
            'target_value_5000', 'target_value_6300', 'target_value_8000', 'target_value_10000'
        ]
        
        for data in queryset:
            # 构建测试值频率数据字典
            test_frequency_data = {}
            target_frequency_data = {}
            
            for field in frequency_fields:
                value = getattr(data, field)
                test_frequency_data[field] = float(value) if value is not None else None
            
            for field in target_fields:
                value = getattr(data, field)
                target_frequency_data[field] = float(value) if value is not None else None
            
            query_data.append({
                'id': data.id,
                'part_name': data.part_name,
                'part_name_label': data.part_name,
                'material_composition': data.material_composition,
                'material_composition_label': data.material_composition,
                'manufacturer': data.manufacturer,
                'manufacturer_label': data.manufacturer if data.manufacturer else None,
                'test_institution': data.test_institution,
                'thickness': float(data.thickness),
                'weight': float(data.weight),
                'test_frequency_data': test_frequency_data,
                'target_frequency_data': target_frequency_data,
                'test_image_path': data.test_image_path,
                'test_date': data.test_date.isoformat() if data.test_date else None,
                'test_location': data.test_location,
                'test_engineer': data.test_engineer,
                'remarks': data.remarks
            })
        
        return Response.success(data=query_data, message="吸声系数查询成功")

    except Exception as e:
        return Response.error(message=f"吸声系数查询失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_test_type_options(request):
    """获取测试类型选项列表"""
    try:
        test_types = [
            {'value': 'vertical', 'label': '垂直入射法'},
            {'value': 'wall_mount', 'label': '上墙法'}
        ]

        serializer = TestTypeOptionSerializer(test_types, many=True)
        return Response.success(data=serializer.data, message="获取测试类型选项成功")

    except Exception as e:
        return Response.error(message=f"获取测试类型选项失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_insulation_part_name_options(request):
    """获取隔声量零件名称选项列表"""
    try:
        # 获取查询参数
        test_type = request.GET.get('test_type')

        # 构建查询条件
        filters = {}
        if test_type:
            filters['test_type'] = test_type

        # 获取不重复的零件名称
        part_names = SoundInsulationCoefficients.objects.filter(**filters).values_list('part_name', flat=True).distinct()

        # 构建选项数据
        options = [{'value': name, 'label': name} for name in part_names if name]

        serializer = InsulationPartNameOptionSerializer(options, many=True)
        return Response.success(data=serializer.data, message="获取零件名称选项成功")

    except Exception as e:
        return Response.error(message=f"获取零件名称选项失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_insulation_material_composition_options(request):
    """获取隔声量材料组成选项列表"""
    try:
        # 获取查询参数
        test_type = request.GET.get('test_type')
        part_name = request.GET.get('part_name')

        # 构建查询条件
        filters = {}
        if test_type:
            filters['test_type'] = test_type
        if part_name:
            filters['part_name'] = part_name

        # 获取不重复的材料组成
        compositions = SoundInsulationCoefficients.objects.filter(**filters).values(
            'material_composition', 'part_name', 'test_type'
        ).distinct()

        # 构建选项数据
        options = []
        for comp in compositions:
            if comp['material_composition']:
                options.append({
                    'value': comp['material_composition'],
                    'label': comp['material_composition'],
                    'part_name': comp['part_name'],
                    'test_type': comp['test_type']
                })

        serializer = InsulationMaterialCompositionOptionSerializer(options, many=True)
        return Response.success(data=serializer.data, message="获取材料组成选项成功")

    except Exception as e:
        return Response.error(message=f"获取材料组成选项失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_insulation_weight_options(request):
    """获取隔声量克重选项列表"""
    try:
        # 获取查询参数
        test_type = request.GET.get('test_type')
        part_name = request.GET.get('part_name')
        material_composition = request.GET.get('material_composition')

        # 构建查询条件
        filters = {}
        if test_type:
            filters['test_type'] = test_type
        if part_name:
            filters['part_name'] = part_name
        if material_composition:
            filters['material_composition'] = material_composition

        # 获取不重复的克重
        weights = SoundInsulationCoefficients.objects.filter(**filters).values(
            'weight', 'part_name', 'material_composition', 'test_type'
        ).distinct()

        # 构建选项数据
        options = []
        for weight in weights:
            if weight['weight']:
                options.append({
                    'value': weight['weight'],
                    'label': f"{weight['weight']}g/m²",
                    'part_name': weight['part_name'],
                    'material_composition': weight['material_composition'],
                    'test_type': weight['test_type']
                })

        serializer = InsulationWeightOptionSerializer(options, many=True)
        return Response.success(data=serializer.data, message="获取克重选项成功")

    except Exception as e:
        return Response.error(message=f"获取克重选项失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def sound_insulation_coefficient_query(request):
    """隔声量系数查询"""
    try:
        # 获取查询参数
        test_type = request.GET.get('test_type')
        part_name = request.GET.get('part_name')
        material_composition = request.GET.get('material_composition')
        weight = request.GET.get('weight')

        # 参数验证 - 至少需要一个查询条件
        if not any([test_type, part_name, material_composition, weight]):
            return Response.error(
                message="至少需要提供一个查询条件",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # 构建查询条件
        filters = {}
        if test_type:
            filters['test_type'] = test_type
        if part_name:
            filters['part_name'] = part_name
        if material_composition:
            filters['material_composition'] = material_composition
        if weight:
            try:
                filters['weight'] = float(weight)
            except ValueError:
                return Response.error(message="克重格式错误", status_code=status.HTTP_400_BAD_REQUEST)

        # 执行查询
        queryset = SoundInsulationCoefficients.objects.filter(**filters)

        if not queryset.exists():
            return Response.success(data=[], message="未找到匹配的隔声量数据")

        # 频率列表
        frequencies = [125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000]

        # 处理查询结果
        query_data = []
        for data in queryset:
            # 测试值频率数据
            test_frequency_data = {}
            for freq in frequencies:
                field_name = f'test_value_{freq}'
                value = getattr(data, field_name, None)
                test_frequency_data[field_name] = float(value) if value is not None else None

            # 目标值频率数据
            target_frequency_data = {}
            for freq in frequencies:
                field_name = f'target_value_{freq}'
                value = getattr(data, field_name, None)
                target_frequency_data[field_name] = float(value) if value is not None else None

            query_data.append({
                'id': data.id,
                'part_name': data.part_name,
                'material_composition': data.material_composition,
                'test_type': data.test_type,
                'test_type_display': data.get_test_type_display(),
                'manufacturer': data.manufacturer,
                'test_institution': data.test_institution,
                'thickness': float(data.thickness) if data.thickness else None,
                'weight': float(data.weight) if data.weight else None,
                'test_frequency_data': test_frequency_data,
                'target_frequency_data': target_frequency_data,
                'test_image_path': data.test_image_path,
                'test_date': data.test_date.isoformat() if data.test_date else None,
                'test_location': data.test_location,
                'test_engineer': data.test_engineer,
                'remarks': data.remarks
            })

        return Response.success(data=query_data, message="隔声量系数查询成功")

    except Exception as e:
        return Response.error(message=f"隔声量系数查询失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def get_material_porosity_part_names(request):
    """获取材料孔隙率流阻的零件名称选项"""
    try:
        # 获取所有不重复的零件名称
        part_names = MaterialPorosityFlowResistance.objects.values_list(
            'part_name', flat=True
        ).distinct().order_by('part_name')

        # 构建选项数据
        options = []
        for part_name in part_names:
            if part_name:  # 过滤空值
                options.append({
                    'value': part_name,
                    'label': part_name
                })

        serializer = MaterialPorosityPartNameOptionSerializer(options, many=True)
        return Response.success(data=serializer.data, message="获取零件名称选项成功")

    except Exception as e:
        return Response.error(message=f"获取零件名称选项失败: {str(e)}")


@api_view(['GET'])
@permission_classes([])  # 临时允许匿名访问用于测试
def material_porosity_query(request):
    """材料孔隙率流阻查询"""
    try:
        # 获取查询参数
        part_names_str = request.GET.get('part_names', '')

        # 构建查询条件
        queryset = MaterialPorosityFlowResistance.objects.all()

        # 如果指定了零件名称，进行筛选
        if part_names_str:
            part_names_list = [name.strip() for name in part_names_str.split(',') if name.strip()]
            if part_names_list:
                queryset = queryset.filter(part_name__in=part_names_list)

        # 按创建时间倒序排列
        queryset = queryset.order_by('-id')

        if not queryset.exists():
            return Response.success(data=[], message="未找到匹配的材料孔隙率流阻数据")

        # 序列化数据
        serializer = MaterialPorosityFlowResistanceSerializer(queryset, many=True)
        return Response.success(data=serializer.data, message="材料孔隙率流阻查询成功")

    except Exception as e:
        return Response.error(message=f"材料孔隙率流阻查询失败: {str(e)}")
