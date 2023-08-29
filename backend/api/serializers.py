import base64

from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Tag, Ingredient, RecipeIngredient,
    Recipe, Subscription, ShoppingCart, Favorite
)
from users.models import CustomUser
from .validators import (
    validate_unique_ingredients, validate_tags, validate_unique_tags
)
from recipes.constants import LIMIT_DIGIT_3


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

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed',
        ]

    def get_is_subscribed(self, obj):
        '''Метод проверки подписки юзера.'''

        request_user = self.context.get('request').user
        return (
            obj.follow.filter(user=request_user).exists() if
            request_user.is_authenticated else False
        )


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Tag.'''

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Ingredient.'''

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit', ]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор ингредиентов в рецепте.'''

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', required=False)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', required=False
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']

    def get_amount(self, ingredient):
        ''''Метод получения количества ингредиента.'''
        recipe_id = self.context.get('recipe_id')
        try:
            recipe_ingredient = ingredient.recipe_ingredients_set.get(
                recipe_id=recipe_id
            )
            return recipe_ingredient.amount
        except RecipeIngredient.DoesNotExist:
            pass
        return None


class RecipeReadSerializer(serializers.ModelSerializer):
    '''Сериализатор для представления модели Recipe.'''

    tags = TagSerializer(many=True)
    author = UserSerializer(default=CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients_set'
    )
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
        ]

    def get_is_favorited(self, recipe):
        '''Метод проверки избранного.'''
        user = self.context.get('request').user
        return (
            user.favorites.filter(recipe=recipe).exists() if
            user.is_authenticated else False
        )

    def get_is_in_shopping_cart(self, recipe):
        '''Метод проверки списка покупок.'''
        user = self.context.get('request').user
        return (
            user.shopping_user.filter(recipe=recipe).exists() if
            user.is_authenticated else False
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    '''Сериализатор для записи модели Recipe.'''

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
            'ingredients', 'tags', 'author',
            'image', 'name', 'text', 'cooking_time',
        ]

    def validate(self, data):
        ingredients_data = data.get('recipe_ingredients_set')
        if not ingredients_data:
            raise serializers.ValidationError(
                'Рецепт не может быть создан без ингредиентов.'
            )

        for ingredient_data in ingredients_data:
            amount = ingredient_data.get('amount')
            if amount is not None and amount <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0.'
                )

        cooking_time = data.get('cooking_time')
        if cooking_time is not None and cooking_time <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0.'
            )

        return data

    def to_representation(self, instance):
        '''Метод переопределения данных.'''
        representation = super().to_representation(instance)
        representation['tags'] = instance.tags.values_list('id', flat=True)
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
        validate_unique_ingredients(ingredients_data)
        tags = validated_data.pop('tags')
        validate_tags(tags),
        validate_unique_tags(tags)

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


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['user', 'recipe']

    def validate(self, data):
        user = self.context['request'].user
        recipe = data['recipe']

        if user == recipe.author:
            raise serializers.ValidationError(
                'Вы не можете добавить свой рецепт в избранное.'
            )

        if recipe.favorites.filter(user=user).exists():
            raise serializers.ValidationError(
                'Данный рецепт уже добавлен в избранное.'
            )

        return data


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
        return (
            obj.author.follow.filter(user=request_user).exists()
            if request_user.is_authenticated else False
        )

    def get_recipes(self, obj):
        '''Метод получения рецептов автора по подписке.'''
        limit = self.context['request'].query_params.get('limit')
        if limit is not None and limit.isdigit():
            limit = int(limit)
        else:
            limit = int(LIMIT_DIGIT_3)
        recipes = obj.author.author_recipes.all()[:limit]
        return ShortListRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        '''Метод получения количества рецептов автора.'''
        return obj.author.author_recipes.count()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    '''Сериализатор создания подписок.'''

    class Meta:
        model = Subscription
        fields = []

    def create(self, validated_data):
        '''Метод создания подписки.'''
        request_user = self.context['request'].user
        user_id = self.context['request'].parser_context['kwargs']['id']
        user_to_subscribe = get_object_or_404(
            CustomUser, id=user_id
        )

        if user_to_subscribe == request_user:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя.'
            )

        if Subscription.objects.filter(
            user=request_user, author=user_to_subscribe
        ).exists():
            raise serializers.ValidationError('Вы уже подписаны на автора.')

        Subscription.objects.create(
            user=request_user,
            author=user_to_subscribe
        )

        recipes = Recipe.objects.filter(author=user_to_subscribe)
        recipes_data = []
        for recipe in recipes:
            recipe_data = {
                'id': recipe.id,
                'name': recipe.name,
                'image': recipe.image.url if recipe.image else '',
                'cooking_time': recipe.cooking_time
            }
            recipes_data.append(recipe_data)

        author_data = {
            'email': user_to_subscribe.email,
            'id': user_to_subscribe.id,
            'username': user_to_subscribe.username,
            'first_name': user_to_subscribe.first_name,
            'last_name': user_to_subscribe.last_name,
            'is_subscribed': True,
            'recipes': recipes_data,
            'recipes_count': len(recipes)
        }

        return author_data


class ShoppingCartSerializer(serializers.ModelSerializer):
    '''Сериализатор для списка покупок.'''

    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже добавлен в список покупок.'
            )
        ]


class ChangePasswordSerializer(serializers.Serializer):
    '''Сериализатор изменения пароля.'''
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def update(self, instance, validated_data):
        '''Метод обновления пароля.'''
        current_password = validated_data.get('current_password')
        new_password = validated_data.get('new_password')

        if current_password == new_password:
            raise serializers.ValidationError(
                'Новый пароль должен отличаться от старого.'
            )
        instance.set_password(new_password)
        instance.save()
        return instance
