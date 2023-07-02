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
        verbose_name = 'Тег',
        verbose_name_plural = 'Теги',
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
        return f'{self.name}, {self.measure_unit}'


class Recepie(models.Model):
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
        upload_to='recepies/',
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
        verbose_name = 'Рецепт',
        verbose_name_plural = 'Рецепты',
        ordering = ('-created_at',)

    def __str__(self) -> str:
        """Строковое представление модели."""
        return self.name


class ShoppingList(models.Model):
    """Модель списка покупок"""

    class Meta:
        """Мета-данные модели."""
        pass

    def __str__(self) -> str:
        """Строковое представление модели."""
        pass
    pass


class Follow(models.Model):
    """Модель подписки на автора."""

    class Meta:
        """Мета-данные модели."""
        pass

    def __str__(self) -> str:
        """Строковое представление модели."""
        pass


class Favorite(models.Model):
    """Модель избранного."""

    class Meta:
        """Мета-данные модели."""
        pass

    def __str__(self) -> str:
        """Строковое представление модели."""
        pass
