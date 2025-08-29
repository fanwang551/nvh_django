"""
OIDC Authentication for Django REST Framework
"""
import logging
import requests
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
from mozilla_django_oidc.utils import import_from_settings
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

logger = logging.getLogger(__name__)
User = get_user_model()


class OIDCUser:
    """
    临时用户对象，用于存储从OIDC token中获取的用户信息
    不会保存到数据库中
    """
    def __init__(self, user_info):
        self.user_info = user_info
        self.id = user_info.get('sub', '')
        self.username = user_info.get('preferred_username', '')
        self.email = user_info.get('email', '')
        self.first_name = user_info.get('given_name', '')
        self.last_name = user_info.get('family_name', '')
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        self.is_staff = False
        self.is_superuser = False

    def __str__(self):
        return f"OIDCUser({self.username})"

    def has_perm(self, perm, obj=None):
        return False

    def has_perms(self, perm_list, obj=None):
        return False

    def has_module_perms(self, module):
        return False


class OIDCAuthentication(authentication.BaseAuthentication):
    """
    OIDC Token Authentication for DRF
    """
    
    def authenticate(self, request):
        """
        从请求头中获取Bearer token并验证
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]
        
        try:
            # 验证token并获取用户信息
            user_info = self.verify_token(token)
            if user_info:
                # 创建临时用户对象
                user = OIDCUser(user_info)
                
                # 将token信息附加到request对象
                request.oidc_token = token
                request.oidc_user_info = user_info
                
                return (user, token)
            else:
                return None
                
        except Exception as e:
            logger.error(f"OIDC authentication error: {e}")
            raise exceptions.AuthenticationFailed('Invalid token')

    def verify_token(self, token):
        """
        验证OIDC token并返回用户信息
        """
        try:
            # 方法1: 使用introspection endpoint验证token
            introspection_result = self.introspect_token(token)
            if introspection_result and introspection_result.get('active'):
                # 获取用户信息
                user_info = self.get_user_info(token)
                return user_info
            
            return None
            
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    def introspect_token(self, token):
        """
        使用Keycloak的introspection endpoint验证token
        """
        try:
            introspection_url = settings.OIDC_OP_TOKEN_ENDPOINT.replace('/token', '/token/introspect')
            
            data = {
                'token': token,
                'client_id': settings.OIDC_RP_CLIENT_ID,
                'client_secret': settings.OIDC_RP_CLIENT_SECRET,
            }
            
            response = requests.post(
                introspection_url,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Token introspection failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Token introspection error: {e}")
            return None

    def get_user_info(self, token):
        """
        从userinfo endpoint获取用户信息
        """
        try:
            response = requests.get(
                settings.OIDC_OP_USER_ENDPOINT,
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Get user info failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Get user info error: {e}")
            return None

    def authenticate_header(self, request):
        """
        返回认证失败时的响应头
        """
        return 'Bearer realm="api"'
