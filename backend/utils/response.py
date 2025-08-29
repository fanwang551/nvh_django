from rest_framework.response import Response as DRFResponse
from rest_framework import status


class Response:
    """
    统一的响应格式
    """
    
    @staticmethod
    def success(data=None, message="操作成功", status_code=status.HTTP_200_OK):
        """成功响应"""
        return DRFResponse({
            "code": 200,
            "message": message,
            "data": data,
            "success": True
        }, status=status_code)
    
    @staticmethod
    def error(message="操作失败", code=400, data=None, status_code=status.HTTP_400_BAD_REQUEST):
        """错误响应"""
        return DRFResponse({
            "code": code,
            "message": message,
            "data": data,
            "success": False
        }, status=status_code)
    
    @staticmethod
    def unauthorized(message="认证失败", data=None):
        """未认证响应"""
        return Response.error(message=message, code=401, data=data, status_code=status.HTTP_401_UNAUTHORIZED)
    
    @staticmethod
    def forbidden(message="没有权限", data=None):
        """禁止访问响应"""
        return Response.error(message=message, code=403, data=data, status_code=status.HTTP_403_FORBIDDEN)
    
    @staticmethod
    def not_found(message="资源不存在", data=None):
        """资源不存在响应"""
        return Response.error(message=message, code=404, data=data, status_code=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def bad_request(message="请求参数错误", data=None):
        """请求错误响应"""
        return Response.error(message=message, code=400, data=data, status_code=status.HTTP_400_BAD_REQUEST)
