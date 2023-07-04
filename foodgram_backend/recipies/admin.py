from django.contrib.admin import register, ModelAdmin

from .models import (
    Tag, Ingredient, Recipie, IngredientInRecipie,
    TagInRecepie, ShoppingList, Follow, Favorite
)


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
