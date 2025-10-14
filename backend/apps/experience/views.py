from django.conf import settings
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from utils.response import Response
from .models import Experience
from .serializers import ExperienceSerializer, ExperienceCreateUpdateSerializer


def _split_keywords(text: str):
    if not text:
        return []
    normalized = text.replace('，', ',').replace('、', ',')
    parts = []
    for token in normalized.split(','):
        token = token.strip()
        if not token:
            continue
        parts.extend([p for p in token.split() if p])
    # 去重但保序
    seen, result = set(), []
    for p in parts:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def experience_list(request):
    """经验数据：查询或创建"""
    if request.method == 'GET':
        queryset = Experience.objects.all()

        # 关键字检索（AND 逻辑，命中 problem_name/keywords/description 任一字段）
        q = request.GET.get('q', '')
        keywords = _split_keywords(q)
        for kw in keywords:
            cond = (
                Q(problem_name__icontains=kw)
                | Q(keywords__icontains=kw)
                | Q(description__icontains=kw)
            )
            queryset = queryset.filter(cond)

        # 分类筛选（精确匹配）
        category = request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)

        queryset = queryset.order_by('-create_time', '-id')

        # 简单分页
        try:
            page = int(request.GET.get('page', '1'))
        except Exception:
            page = 1

        default_page_size = 20
        try:
            default_page_size = int(settings.REST_FRAMEWORK.get('PAGE_SIZE', 20))
        except Exception:
            pass

        try:
            page_size = int(request.GET.get('page_size', str(default_page_size)))
        except Exception:
            page_size = default_page_size

        total = queryset.count()
        start = max(0, (page - 1) * page_size)
        end = start + page_size
        items = queryset[start:end]

        serializer = ExperienceSerializer(items, many=True)
        return Response.success(
            data={
                'items': serializer.data,
                'total': total,
                'page': page,
                'page_size': page_size,
            },
            message='获取经验数据成功'
        )

    # POST 创建
    serializer = ExperienceCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        output = ExperienceSerializer(instance).data
        return Response.success(data=output, message='创建经验数据成功', status_code=201)

    return Response.error(message='创建经验数据失败', data=serializer.errors)


@api_view(['GET'])
@permission_classes([AllowAny])
def experience_detail(request, pk: int):
    """经验数据详情"""
    try:
        instance = Experience.objects.get(pk=pk)
    except Experience.DoesNotExist:
        return Response.not_found(message='经验数据不存在')

    serializer = ExperienceSerializer(instance)
    return Response.success(data=serializer.data, message='获取经验详情成功')

