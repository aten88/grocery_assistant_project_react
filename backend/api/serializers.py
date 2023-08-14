import base64

from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from recipes.models import (
    Tag, Ingredient, RecipeIngredient,
    Recipe, Subscription, ShoppingCart, Favorite
)


class Base64ImageField(serializers.ImageField):
    '''Кастомное поле для кодирования изображений.'''

    def to_internal_value(self, data):
        '''Метод декодирования картинки.'''
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    '''Сериализатор модели User.'''

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username',
            'first_name', 'last_name',
        ]


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Tag.'''

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Ingredient.'''

    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit', 'amount', ]

    def get_amount(self, ingredient):
        ''''Метод получения количества ингредиента.'''
        recipe_id = self.context.get('recipe_id')
        try:
            recipe_ingredient = RecipeIngredient.objects.get(
                ingredient=ingredient, recipe_id=recipe_id
            )
            return recipe_ingredient.amount
        except RecipeIngredient.DoesNotExist:
            pass
        return None


class RecipeIngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор ингредиеентов в рецепте.'''

    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Recipe.'''

    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients_set'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer(default=CurrentUserDefault())
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'author', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time', 'is_in_shopping_cart',
            'is_favorited',
        ]

    def to_representation(self, instance):
        '''Метод переопределения данных.'''
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(), many=True
        ).data
        return representation

    def create_recipe_ingredients(self, recipe, ingredients_data):
        '''Метод оптимизации создания обьектов'''
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient_data['ingredient']['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        '''Метод создания рецепта.'''
        ingredients_data = validated_data.pop('recipe_ingredients_set')
        tags = validated_data.pop('tags')

        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data)
            recipe.tags.add(*tags)
            self.create_recipe_ingredients(recipe, ingredients_data)

        return recipe

    def update(self, recipe, validated_data):
        '''Метод обновления рецепта.'''
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time
        )

        tags = validated_data.get('tags', recipe.tags.all())
        recipe.tags.set(tags)

        ingredients_data = validated_data.get('recipe_ingredients_set', [])

        with transaction.atomic():
            RecipeIngredient.objects.filter(recipe=recipe).delete()
            self.create_recipe_ingredients(recipe, ingredients_data)

            recipe.save()

        return recipe

    def get_is_in_shopping_cart(self, recipe):
        '''Метод проверки списка покупок.'''
        user = self.context.get('request').user
        return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()

    def get_is_favorited(self, recipe):
        '''Метод проверки избранного.'''
        user = self.context.get('request').user
        return Favorite.objects.filter(user=user, recipe=recipe).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['user', 'recipe']


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для отображения избранного рецепта.'''

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class UserDetailSerializer(serializers.ModelSerializer):
    '''Сериализатор модели User по id.'''

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
        '''Метод проверки подписки юзера.'''

        request_user = self.context.get('request').user
        return (
            request_user.is_authenticated
            and Subscription.objects.filter(
                author=obj.id, user=request_user
            ).exists()
        )


class ShortListRecipeSerializer(serializers.ModelSerializer):
    '''Краткий сериализатор рецепта.'''
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerialiazer(serializers.ModelSerializer):
    '''Сериализатор модели подписок.'''
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        '''Метод проверки подписки юзера.'''

        request_user = self.context.get('request').user
        if request_user.is_authenticated:
            return Subscription.objects.filter(
                author=obj.author, user=request_user
            ).exists()
        return False

    def get_recipes(self, obj):
        '''Метод получения рецептов автора по подписке.'''
        recipes = Recipe.objects.filter(author=obj.author)
        serializer = ShortListRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        '''Метод получения количества рецептов автора.'''
        return Recipe.objects.filter(author=obj.author).count()


class ShoppingCartSerializer(serializers.ModelSerializer):
    '''Сериализатор для списка покупок.'''

    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']


class RecipeSerializerDetail(serializers.ModelSerializer):
    '''Сериализатор модели Recipe по ID.'''

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
        '''Метод проверки рецепта в избранном у текущего пользователя.'''

        request_user = self.context.get('request').user
        if request_user.is_authenticated:
            return Favorite.objects.filter(
                recipe=obj, user=request_user
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        '''Метод проверки рецепта в списке покупок у текущего пользователя.'''

        request_user = self.context.get('request').user
        if request_user.is_authenticated:
            return ShoppingCart.objects.filter(
                recipe=obj, user=request_user
            ).exists()
        return False


class SubscriptionCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def create(self, validated_data):
        """Метод создания подписки."""
        request_user = self.context['request'].user
        user_to_subscribe = get_object_or_404(User, id=validated_data['id'])

        if user_to_subscribe == request_user:
            raise serializers.ValidationError(
                "Вы не можете подписаться на себя."
            )

        if Subscription.objects.filter(
            user=request_user, author=user_to_subscribe
        ).exists():
            raise serializers.ValidationError("Вы уже подписаны на автора.")

        Subscription.objects.create(
            user=request_user,
            author=user_to_subscribe
        )

        author_data = {
            'email': user_to_subscribe.email,
            'username': user_to_subscribe.username,
            'first_name': user_to_subscribe.first_name,
            'last_name': user_to_subscribe.last_name,
            'is_subscribed': True,
            'recipes': [],
            'recipes_count': 0
        }

        return author_data
