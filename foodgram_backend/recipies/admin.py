from django.contrib.admin import register, ModelAdmin

from .models import (
    Tag, Ingredient, Recipie, IngredientInRecipie,
    TagInRecepie, ShoppingList, Follow, Favorite
)


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug',)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'measure_unit',)
    search_fields = ('name',)


@register(Recipie)
class RecipieAdmin(ModelAdmin):
    list_display = (
        'pk', 'name', 'author', 'get_favorites', 'get_tags', 'created_at',
    )
    list_filter = ('author', 'name', 'tags',)
    search_fields = ('name',)

    def get_favorites(self, obj):
        return obj.favorites.count()

    get_favorites.short_description = (
        'Количество добавлений рецепта в избранное'
    )

    def get_tags(self, obj):
        return '\n'.join(obj.tags.values_list('name', flat=True))

    get_tags.short_description = ('Тег или список тегов')


@register(IngredientInRecipie)
class IngredientInRecipieAdmin(ModelAdmin):
    list_display = ('pk', 'recipie', 'ingredient', 'amount',)


@register(TagInRecepie)
class TagInRecepieAdmin(ModelAdmin):
    list_display = ('pk', 'tag', 'recipie', )


@register(ShoppingList)
class ShoppingListAdmin(ModelAdmin):
    list_display = ('pk', 'user', 'recipie',)


@register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = ('pk', 'user', 'author',)
    search_fields = ('user', 'author',)
    list_filter = ('user', 'author',)


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('pk', 'user', 'recipie',)
