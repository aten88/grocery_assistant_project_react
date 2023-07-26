import base64

from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from rest_framework import serializers


from recipes.models import (
    Tag, Ingredient,
    Recipe, Subscription, ShoppingCart, Favorite
)


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для кодирования изображений."""

    def to_internal_value(self, data):
        """Метод декодирования картинки."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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

    ingredients = IngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = [
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
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
            'first_name', 'last_name',
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    """Сериализатор модели User по id."""

    email = serializers.EmailField(required=True, max_length=254)
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        """Метод проверки подписки юзера."""

        request_user = self.context.get('request').user
        if request_user.is_authenticated:
            return Subscription.objects.filter(
                author=obj.id, user=request_user
            ).exists()
        return False


class SubscriptionSerialiazer(serializers.ModelSerializer):
    """Сериализатор модели подписок."""
    author = serializers.SerializerMethodField()
    recipe = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ['author', 'recipe']

    def get_author(self, obj):
        """Метод получения имени автора."""
        return obj.author.username

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


class RecipeSerializerDetail(serializers.ModelSerializer):
    """Сериализатор модели Recipe по ID."""

    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    author = UserDetailSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        ]

    def get_is_favorited(self, obj):
        """Метод проверки рецепта в избранном у текущего пользователя."""

        request_user = self.context.get('request').user
        if request_user.is_authenticated:
            return Favorite.objects.filter(
                recipe=obj, user=request_user
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Метод проверки рецепта в списке покупок у текущего пользователя."""

        request_user = self.context.get('request').user
        if request_user.is_authenticated:
            return ShoppingCart.objects.filter(
                recipe=obj, user=request_user
            ).exists()
        return False
