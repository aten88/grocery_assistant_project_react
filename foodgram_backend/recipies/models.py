from django.contrib.auth import get_user_model
from django.core.validators import (MinValueValidator, RegexValidator)
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель описания тега."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название тега'
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение цвета, не является форматом HEX!'
            )
        ],
        default='#49B64E',
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Уникальный слаг'
    )

    class Meta:
        """Мета-данные тега."""

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'color', 'slug'),
                name='unique_tags',
            ),
        )

    def __str__(self) -> str:
        """Строковое представление модели."""

        return self.name


class Ingredient(models.Model):
    """Модель описания ингредиента."""

    name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='Название ингредиента'

    )
    quantity = models.IntegerField(
        verbose_name='Количество'
    )
    measure_unit = models.CharField(
        max_length=100,
        verbose_name='Единица измерения'
    )

    class Meta:
        """Мета-данные ингредиента."""

        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        """Строковое представление модели."""

        return f'{self.name} {self.measure_unit}'


class Recipie(models.Model):
    """Модель описания рецепта."""

    author = models.ForeignKey(
        User,
        related_name='recipies',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=150,
        verbose_name='Название рецепта'
    )
    picture = models.ImageField(
        upload_to='recipies/',
        blank=True,
        verbose_name='Картинка блюда'
    )
    text = models.TextField(
        max_length=2000,
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipie',
        related_name='recipies',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipies',
        verbose_name='Тег'
    )
    time_cooking = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message='Не может быть меньше 1!'),
        ]
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        """Мета-данные модели."""

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        """Строковое представление модели."""

        return self.name


class IngredientInRecipie(models.Model):
    """Модель ингредиентов в отдельном рецепте."""

    recipie = models.ForeignKey(
        Recipie,
        on_delete=models.CASCADE,
        related_name='ingrdients_list',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient_in_recepie',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(1, message='Не может быть меньше 1!'),
        ]
    )

    class Meta:
        """Мета-данные модели."""

        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=('recipie', 'ingredient'),
                name='unique_ingredients_in_recepies'
            )
        ]

    def __str__(self) -> str:
        """Строковое представление модели."""

        return f'{self.recipie} {self.ingredient}'


class TagInRecepie(models.Model):
    """Модель тегов рецептов."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Теги',
        help_text='Выберите рецепт'
    )
    recipie = models.ForeignKey(
        Recipie,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт'
    )

    class Meta:
        """Мета-данные модели."""

        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        constraints = [
            models.UniqueConstraint(fields=['tag', 'recipie'],
                                    name='unique_tag_recipie')
        ]

    def __str__(self) -> str:
        """Строковое представление модели."""

        return f'{self.tag} {self.recipie}'


class ShoppingList(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Пользователь'
    )
    recipie = models.ForeignKey(
        Recipie,
        on_delete=models.CASCADE,
        related_name='shopping_recepie',
        verbose_name='Рецепт'
    )

    class Meta:
        """Мета-данные модели."""

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipie'], name='unique_shoppinglist'
            )
        ]

    def __str__(self) -> str:
        """Строковое представление модели."""

        return f'{self.user} {self.recipie}'


class Follow(models.Model):
    """Модель подписки на автора."""

    author = models.ForeignKey(
        User,
        related_name='follow',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    class Meta:
        """Мета-данные модели."""

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            )
        ]

    def __str__(self) -> str:
        """Строковое представление модели."""

        return f'{self.user} {self.author}'


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )
    recipie = models.ForeignKey(
        Recipie,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        """Мета-данные модели."""

        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipie'], name='unique_favorite'
            )
        ]

    def __str__(self) -> str:
        """Строковое представление модели."""

        return f'{self.user} {self.recipie}'
