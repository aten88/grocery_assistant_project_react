from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (
    RegexValidator, MinValueValidator, MaxValueValidator
)
from django.core.exceptions import ValidationError

from .constants import MIN_COOKING_TIME, MAX_COOKING_TIME


def unique_color_validator(value):
    """Кастомный валидатор для проверки уникальности HEX-кода цвета."""

    if Tag.objects.filter(color=value).exists():
        raise ValidationError("HEX-код цвета должен быть уникальным.")


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=200,
        verbose_name="Название Тега.",
        unique=True
    )
    color = models.CharField(
        max_length=7,
        verbose_name="HEX-код цвета.",
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^#[0-9A-Fa-f]{6}$',
                message="Введите HEX-код цвета в формате #RRGGBB.",
                code='invalid_color_format'
            ),
            unique_color_validator,
        ],
        help_text="Введите HEX-код цвета в формате #RRGGBB."
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="Слаг."
    )

    class Meta:
        "Мета-данные модели."

        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self) -> str:
        """Метод строкового представления модели."""

        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        max_length=200,
        verbose_name="Название ингредиента"
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name="Единица измерения"
    )

    class Meta:
        "Мета-данные модели."
        unique_together = ('name', 'measurement_unit')
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def clean(self):
        """Метод валидации данных перед сохранением."""
        existing_ingredient = Ingredient.objects.filter(
            name=self.name,
            measurement_unit=self.measurement_unit
        ).first()

        if existing_ingredient and existing_ingredient.pk != self.pk:
            raise ValidationError(
                "Такой ингредиент с такой единицей измерения уже существует."
            )

    def __str__(self) -> str:
        """Метод строкового представления модели."""

        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта."
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта.",
        unique=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        related_name='recipes'
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        blank=True,
        null=True,
        default=None,
        verbose_name="Фото рецепта."
    )
    text = models.TextField(
        verbose_name="Подробное описание рецепта."
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Название тега."
    )
    cooking_time = models.PositiveBigIntegerField(
        verbose_name="Время приготовления.",
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message="Время приготовления должно быть больше 0."
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message="Время приготовления должно быть меньше 3 суток."
            )
        ]
    )
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Дата публикации."
    )

    class Meta:
        "Мета-данные модели."

        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-created",)

    def __str__(self) -> str:
        """Метод строкового представления модели."""

        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients_set'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Количество ингредиента'
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"

    def __str__(self) -> str:
        """Метод строкового представления модели."""
        return f'Ингредиент {self.ingredient} в рецепте {self.recipe}'


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="favorites"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="favorites"
    )

    class Meta:
        "Мета-данные модели."

        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"

    def clean(self):
        """Метод валидации данных перед сохранением."""
        if self.recipe.author == self.user:
            raise ValidationError(
                "Вы не можете добавить свой рецепт в избранное."
            )

    def validate_unique(self, exclude=None):
        """Метод для проверки уникальности данных перед сохранением."""
        super().validate_unique(exclude)

        if Favorite.objects.filter(
            user=self.user, recipe=self.recipe
        ).exists():
            raise ValidationError("Этот рецепт уже добавлен в избранное.")

    def __str__(self) -> str:
        """Метод строкового представления модели."""
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class Subscription(models.Model):
    """Модель подписки на автора."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='follow'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower'
    )

    class Meta:
        "Мета-данные модели."
        unique_together = ('author', 'user')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        """Метод строкового представления модели."""
        return (
            f'Пользователь {self.user} подписан на {self.author}'
        )

    def clean(self):
        """Метод валидации данных перед сохранением."""
        if self.user == self.author:
            raise ValidationError("Вы не можете подписаться на самого себя.")


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
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
        "Мета-данные модели."
        unique_together = ('user', 'recipe')
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self) -> str:
        """Метод строкового представления модели."""
        return f'{self.recipe} добавлен в список покупок {self.user}'
