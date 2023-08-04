import base64

from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault


from recipes.models import (
    Tag, Ingredient, RecipeIngredient,
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


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username',
            'first_name', 'last_name',
        ]


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient."""

    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit', 'amount', ]

    def get_amount(self, ingredient):
        recipe_id = self.context.get('recipe_id')
        if recipe_id:
            try:
                recipe_ingredient = RecipeIngredient.objects.get(
                    ingredient=ingredient,
                    recipe_id=recipe_id
                )
                return recipe_ingredient.amount
            except RecipeIngredient.DoesNotExist:
                pass
        return None


class RecipeIngredientSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe."""

    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients_set'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer(default=CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = [
            'id', 'author', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        ]

    def create(self, validated_data):
        """Метод создания рецепта."""
        ingredients_data = validated_data.pop('recipe_ingredients_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.add(*tags)
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_data['ingredient']['id'],
                amount=ingredient_data['amount']
            )
        return recipe

    def update(self, recipe, validated_data):
        """Метод обновления рецепта."""
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time
        )

        tags = validated_data.get('tags', recipe.tags.all())
        recipe.tags.set(tags)

        ingredients_data = validated_data.get('recipe_ingredients_set', [])
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_data['ingredient']['id'],
                amount=ingredient_data['amount']
            )

        recipe.save()
        return recipe


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения избранного рецепта."""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


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
    email = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'email', 'id', 'first_name', 'last_name', 'is_subscribed',
            'recipes', 'recipes_count'
        ]

    def get_email(self, obj):
        """Метод получения email автора."""
        return obj.author.email

    def get_first_name(self, obj):
        """Метод получения имени автора."""
        return obj.author.first_name

    def get_last_name(self, obj):
        """Метод получения фамилии автора."""
        return obj.author.last_name

    def get_is_subscribed(self, obj):
        """Метод проверки подписки юзера."""

        request_user = self.context.get('request').user
        if request_user.is_authenticated:
            return Subscription.objects.filter(
                author=obj.id, user=request_user
            ).exists()
        return False

    def get_recipes(self, obj):
        """Метод получения рецептов автора по подписке."""
        recipes = Recipe.objects.filter(author=obj.author)
        serializer = RecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Метод получения количества рецептов автора."""
        return Recipe.objects.filter(author=obj.author).count()


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
            'name', 'image', 'text', 'cooking_time',
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
