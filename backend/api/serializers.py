from django.contrib.auth.models import User
from rest_framework import serializers

from recipes.models import (
    Tag, Ingredient,
    Recipe, Subscription, ShoppingCart
)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe."""

    class Meta:
        model = Recipe
        fields = [
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        ]


class RecipeSerializerDetail(serializers.ModelSerializer):
    """Сериализатор модели Recipe по ID."""

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        ]


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения избранного рецепта."""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""

    email = serializers.EmailField(required=True, max_length=254)
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username',
            'first_name', 'last_name'
        ]


class SubscriptionSerialiazer(serializers.ModelSerializer):
    """Сериализатор модели подписок."""
    author = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    recipe = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ['author', 'user', 'recipe']

    def get_author(self, obj):
        """Метод получения имени автора."""
        return obj.author.username

    def get_user(self, obj):
        """Метод получения имени юзера."""
        return obj.user.username

    def get_recipe(self, obj):
        """Метод получения рецептов автора по подписке."""

        author = obj.author
        recipes = Recipe.objects.filter(author=author)
        serializer = RecipeSerializer(recipes, many=True)

        return serializer.data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']
