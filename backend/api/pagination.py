from rest_framework.pagination import PageNumberPagination

from recipes.constants import PAGE_SIZE


class CustomPagination(PageNumberPagination):
    '''Кастомный пагинатор.'''
    page_size = PAGE_SIZE
    page_size_query_param = 'page_size'
