from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.core.validators import (
    MaxValueValidator, MinValueValidator, RegexValidator
)

from users.models import CustomUser
from .constants import (
    LIMIT_COLOR_FIELD, LIMIT_DIGITS_AMOUNT_FIELD,
    LIMIT_MODEL_FIELD, LIMIT_NUMBER_WIDTH, MAX_COOKING_TIME,
    MAX_LENGTH, MAX_LENGTH_NAME_FIELD, MIN_COOKING_TIME
)
from .validators import unique_color_validator


class Tag(models.Model):
    '''Модель тега.'''

    name = models.CharField(
        max_length=MAX_LENGTH_NAME_FIELD,
        verbose_name='Название Тега.',
        unique=True
    )
    color = models.CharField(
        max_length=LIMIT_COLOR_FIELD,
        verbose_name='HEX-код цвета.',
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^#[0-9A-Fa-f]{6}$',
                message='Введите HEX-код цвета в формате #RRGGBB.',
                code='invalid_color_format'
            ),
            unique_color_validator,
        ],
        help_text='Введите HEX-код цвета в формате #RRGGBB.'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH,
        unique=True,
        verbose_name='Слаг.'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    '''Модель ингредиента.'''

    name = models.CharField(
        max_length=MAX_LENGTH_NAME_FIELD,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=LIMIT_MODEL_FIELD,
        verbose_name='Единица измерения'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    '''Модель рецепта.'''

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта.',
        related_name='author_recipes'
    )
    name = models.CharField(
        max_length=MAX_LENGTH_NAME_FIELD,
        verbose_name='Название рецепта.',
        unique=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        related_name='recipes'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=True,
        null=True,
        default=None,
        verbose_name='Фото рецепта.'
    )
    text = models.TextField(
        verbose_name='Подробное описание рецепта.'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Название тега.'
    )
    cooking_time = models.PositiveBigIntegerField(
        verbose_name='Время приготовления.',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message='Время приготовления должно быть больше 0.'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message='Время приготовления должно быть меньше 3 суток.'
            )
        ]
    )
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации.'
    )

    def total_favorites(self):
        '''Метод для получения количества добавлений рецепта в избранное.'''
        return self.favorites.count()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created',)

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    '''Модель ингредиета в рецепте.'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients_set'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipe_ingredients_set'
    )
    amount = models.DecimalField(
        max_digits=LIMIT_DIGITS_AMOUNT_FIELD,
        decimal_places=LIMIT_NUMBER_WIDTH,
        verbose_name='Количество ингредиента'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self) -> str:
        return f'Ингредиент {self.ingredient} в рецепте {self.recipe}'


class Favorite(models.Model):
    '''Модель избранного.'''

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorites'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def clean(self):
        '''Метод валидации данных перед сохранением.'''
        if self.recipe.author == self.user:
            raise ValidationError(
                'Вы не можете добавить свой рецепт в избранное.'
            )

    def __str__(self) -> str:
        '''Метод строкового представления модели.'''
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class Subscription(models.Model):
    '''Модель подписки на автора.'''

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='follow'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscription'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return (
            f'Пользователь {self.user} подписан на {self.author}'
        )


class ShoppingCart(models.Model):
    '''Модель списка покупок.'''

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self) -> str:
        return f'{self.recipe} добавлен в список покупок {self.user}'
