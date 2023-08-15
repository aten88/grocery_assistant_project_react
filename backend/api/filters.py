from django_filters import rest_framework, filters
from django_filters.rest_framework import FilterSet

from recipes.models import Ingredient, Tag, Recipe


class IngredientFilter(FilterSet):
    '''Фильтр для поиска по названию ингредиента.'''

    name = rest_framework.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(FilterSet):
    '''Фильтр для избранного и списка покупок.'''
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug')
    is_favorited = filters.NumberFilter(
        method='common_filter',
        field_name='favorites__user_id')
    is_in_shopping_cart = filters.NumberFilter(
        method='common_filter',
        field_name='shopping_recipe__user_id')

    def common_filter(self, queryset, name, value):
        if value:
            return queryset.filter(**{name: self.request.user})
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
