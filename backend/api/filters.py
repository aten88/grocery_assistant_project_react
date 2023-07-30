from django_filters.rest_framework import FilterSet
from django_filters import rest_framework

from recipes.models import Ingredient


class IngredientFilter(FilterSet):
    """Поиск по названию ингредиента."""

    name = rest_framework.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
