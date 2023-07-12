from django.contrib.auth.models import User

from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, Favorite


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag."""

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели Favorite."""

    class Meta:
        model = Favorite
        fields = ['user', 'recipe']


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
