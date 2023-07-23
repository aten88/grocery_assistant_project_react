from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Кастомный пагинатор на 6 обьектов."""
    page_size = 6
    page_size_query_param = 'page_size'
