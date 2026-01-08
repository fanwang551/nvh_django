"""
用户相关视图 - 基于mozilla-django-oidc的标准实现
"""

import logging

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .authentication import OIDCAuthentication


logger = logging.getLogger(__name__)

User = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """健康检查接口"""
    return Response(
        {
            'status': 'ok',
            'message': 'Users API is running with OIDC authentication',
            'authentication': 'mozilla-django-oidc',
        }
    )


@api_view(['GET'])
@authentication_classes([OIDCAuthentication])
@permission_classes([])
def user_info(request):
    """获取当前用户信息"""
    try:
        user = request.user

        # 获取OIDC相关信息
        oidc_user_info = getattr(request, 'oidc_user_info', {})
        is_authenticated = bool(getattr(user, 'is_authenticated', False))

        # 统一提取用户基础字段
        username = getattr(user, 'username', '') if is_authenticated else oidc_user_info.get('preferred_username', '')
        email = getattr(user, 'email', '') if is_authenticated else oidc_user_info.get('email', '')
        first_name = getattr(user, 'first_name', '') if is_authenticated else oidc_user_info.get('given_name', '')
        last_name = getattr(user, 'last_name', '') if is_authenticated else oidc_user_info.get('family_name', '')

        # 首次登录自动落库（仅在有 username 时执行）
        if username:
            try:
                with transaction.atomic():
                    user_obj, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': email or '',
                            'first_name': first_name or '',
                            'last_name': last_name or '',
                            'is_active': True,
                        },
                    )
                    if created:
                        user_obj.set_password('sgmw5050')
                        user_obj.save(update_fields=['password'])
            except IntegrityError:
                # 并发场景下可能已由其他请求创建，忽略即可
                pass

        response_data = {
            'user': {
                'id': getattr(user, 'id', '') if is_authenticated else oidc_user_info.get('sub', ''),
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_authenticated': is_authenticated,
                'is_active': getattr(user, 'is_active', False) if is_authenticated else False,
            },
            'oidc_info': {
                'sub': oidc_user_info.get('sub', ''),
                'preferred_username': oidc_user_info.get('preferred_username', ''),
                'email': oidc_user_info.get('email', ''),
                'email_verified': oidc_user_info.get('email_verified', False),
                'given_name': oidc_user_info.get('given_name', ''),
                'family_name': oidc_user_info.get('family_name', ''),
                'name': oidc_user_info.get('name', ''),
            },
        }

        return Response(response_data)

    except Exception as e:
        logger.error(f"User info error: {e}")
        return Response(
            {'error': f'获取用户信息失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@authentication_classes([OIDCAuthentication])
@permission_classes([])
def user_profile(request):
    """获取用户详细资料"""
    try:
        user = request.user
        oidc_user_info = getattr(request, 'oidc_user_info', {})
        is_authenticated = bool(getattr(user, 'is_authenticated', False))

        profile_data = {
            'basic_info': {
                'username': getattr(user, 'username', '') if is_authenticated else oidc_user_info.get('preferred_username', ''),
                'email': getattr(user, 'email', '') if is_authenticated else oidc_user_info.get('email', ''),
                'first_name': getattr(user, 'first_name', '') if is_authenticated else oidc_user_info.get('given_name', ''),
                'last_name': getattr(user, 'last_name', '') if is_authenticated else oidc_user_info.get('family_name', ''),
                'full_name': oidc_user_info.get('name', ''),
            },
            'account_info': {
                'user_id': oidc_user_info.get('sub', ''),
                'preferred_username': oidc_user_info.get('preferred_username', ''),
                'email_verified': oidc_user_info.get('email_verified', False),
            },
            'permissions': {
                'is_authenticated': is_authenticated,
                'is_active': getattr(user, 'is_active', False) if is_authenticated else False,
                'is_staff': getattr(user, 'is_staff', False) if is_authenticated else False,
                'is_superuser': getattr(user, 'is_superuser', False) if is_authenticated else False,
            },
        }

        return Response(profile_data)

    except Exception as e:
        logger.error(f"User profile error: {e}")
        return Response(
            {'error': f'获取用户资料失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@permission_classes([])
def auth_test(request):
    """OIDC认证测试端点"""
    try:
        user = request.user
        oidc_token = getattr(request, 'oidc_token', '')
        oidc_user_info = getattr(request, 'oidc_user_info', {})

        response_data = {
            'message': '✅ OIDC认证测试成功！',
            'authentication_method': 'mozilla-django-oidc',
            'user_info': {
                'type': type(user).__name__,
                'id': getattr(user, 'id', oidc_user_info.get('sub', '')),
                'username': user.username,
                'email': user.email,
                'is_authenticated': user.is_authenticated,
                'is_active': user.is_active,
            },
            'oidc_info': {
                'has_token': bool(oidc_token),
                'token_length': len(oidc_token) if oidc_token else 0,
                'user_info': oidc_user_info,
            },
            'request_info': {
                'path': request.path,
                'method': request.method,
                'has_oidc_token': hasattr(request, 'oidc_token'),
                'has_oidc_user_info': hasattr(request, 'oidc_user_info'),
            },
        }

        return Response(response_data)

    except Exception as e:
        logger.error(f"Auth test error: {e}")
        return Response(
            {'error': f'认证测试失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@authentication_classes([OIDCAuthentication])
@permission_classes([])
def user_groups(request):
    """获取当前登录用户的分组信息（group names）及相关权限标记"""
    try:
        oidc_user_info = getattr(request, 'oidc_user_info', {}) or {}

        username = getattr(request.user, 'username', '') or oidc_user_info.get('preferred_username', '')
        email = getattr(request.user, 'email', '') or oidc_user_info.get('email', '')
        first_name = getattr(request.user, 'first_name', '') or oidc_user_info.get('given_name', '')
        last_name = getattr(request.user, 'last_name', '') or oidc_user_info.get('family_name', '')

        if not username:
            return Response(
                {
                    'user': {
                        'id': '',
                        'username': '',
                        'email': '',
                        'first_name': '',
                        'last_name': '',
                    },
                    'group_names': [],
                    'permissions': {
                        'is_nvh_group_leader': False,
                        'has_scheduler_whitelist': False,
                    },
                }
            )

        try:
            with transaction.atomic():
                user_obj, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email or '',
                        'first_name': first_name or '',
                        'last_name': last_name or '',
                        'is_active': True,
                    },
                )
                if created:
                    user_obj.set_password('sgmw5050')
                    user_obj.save(update_fields=['password'])
        except IntegrityError:
            user_obj = User.objects.filter(username=username).first()

        if not user_obj:
            return Response(
                {'error': '用户不存在且创建失败'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        group_names = list(user_obj.groups.values_list('name', flat=True))
        is_nvh_group_leader = 'NVH组组长' in group_names

        return Response(
            {
                'user': {
                    'id': user_obj.id,
                    'username': username,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                },
                'group_names': group_names,
                'permissions': {
                    'is_nvh_group_leader': is_nvh_group_leader,
                    'has_scheduler_whitelist': is_nvh_group_leader,
                },
            }
        )

    except Exception as e:
        logger.error(f"User groups error: {e}")
        return Response(
            {'error': f'获取用户分组失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def users_by_group(request):
    """
    按 Django auth Group 查询用户列表（用于前端下拉选择）

    请求：
      - method: GET
      - query params:
          - group_name: 分组名称（默认：NVH组组员）
          - keyword: 可选，模糊匹配 username/first_name/last_name

    返回：
      {
        "group_name": "NVH组组员",
        "items": [
          {"id": 1, "username": "user1", "full_name": "张三", "group_names": ["NVH组组员"]}
        ]
      }
    """
    try:
        group_name = request.GET.get('group_name') or 'NVH组组员'
        keyword = (request.GET.get('keyword') or '').strip()

        queryset = User.objects.filter(groups__name=group_name, is_active=True).prefetch_related('groups').distinct()
        if keyword:
            queryset = queryset.filter(
                Q(username__icontains=keyword) | Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword)
            )
        queryset = queryset.order_by('username', 'id')

        items = []
        for u in queryset:
            group_names = list(u.groups.values_list('name', flat=True))
            full_name = f"{u.last_name or ''}{u.first_name or ''}".strip() or u.username
            items.append(
                {
                    'id': u.id,
                    'username': u.username,
                    'full_name': full_name,
                    'group_names': group_names,
                }
            )

        return Response({'group_name': group_name, 'items': items})
    except Exception as e:
        logger.error(f"Users by group error: {e}")
        return Response(
            {'error': f'获取分组用户失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
