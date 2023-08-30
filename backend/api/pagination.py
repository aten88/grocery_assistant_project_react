from rest_framework.pagination import PageNumberPagination

from recipes.constants import PAGE_SIZE_PAGINATION


class CustomPagination(PageNumberPagination):
    '''Кастомный пагинатор.'''
    page_size = PAGE_SIZE_PAGINATION
    page_size_query_param = 'page_size'
