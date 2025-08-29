from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageNumberPaginationUtil(PageNumberPagination):
    """
    自定义分页器
    """
    # 每页的默认显示数据量
    page_size = 10

    # URL参数中设置每页展示数量的名称
    page_size_query_param = 'page_size'

    # URL参数中设置页码的名称
    page_query_param = 'page'

    # 每页的最大数据量
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        重写分页响应方法

        Args:
            data: 分页数据

        Returns:
            Response: 分页响应
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'current': self.page.number,
            'max_page': self.page.paginator.num_pages,
            'results': data
        })
