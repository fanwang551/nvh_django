"""
用户相关视图 - 基于mozilla-django-oidc的标准实现
"""
import logging
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """健康检查接口"""
    return Response({
        'status': 'ok',
        'message': 'Users API is running with OIDC authentication',
        'authentication': 'mozilla-django-oidc'
    })


@api_view(['GET'])
@permission_classes([])
def user_info(request):
    """获取当前用户信息"""
    try:
        user = request.user
        
        # 获取OIDC相关信息
        oidc_user_info = getattr(request, 'oidc_user_info', {})
        is_authenticated = bool(getattr(user, 'is_authenticated', False))
        
        response_data = {
            'user': {
                'id': getattr(user, 'id', '') if is_authenticated else oidc_user_info.get('sub', ''),
                'username': getattr(user, 'username', '') if is_authenticated else oidc_user_info.get('preferred_username', ''),
                'email': getattr(user, 'email', '') if is_authenticated else oidc_user_info.get('email', ''),
                'first_name': getattr(user, 'first_name', '') if is_authenticated else oidc_user_info.get('given_name', ''),
                'last_name': getattr(user, 'last_name', '') if is_authenticated else oidc_user_info.get('family_name', ''),
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
            }
        }
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"User info error: {e}")
        return Response(
            {'error': f'获取用户信息失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
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
            }
        }
        
        return Response(profile_data)
        
    except Exception as e:
        logger.error(f"User profile error: {e}")
        return Response(
            {'error': f'获取用户资料失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
            }
        }

        return Response(response_data)

    except Exception as e:
        logger.error(f"Auth test error: {e}")
        return Response(
            {'error': f'认证测试失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )