from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=200,
        verbose_name="Название Тега.",
        unique=True
    )
    color_code = models.CharField(
        max_length=7,
        verbose_name="HEX-код цвета.",
        unique=True
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
        verbose_name="Название ингредиента."
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    measure_units = models.CharField(
        max_length=50
    )

    class Meta:
        """Мета данные модели."""

        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

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
        verbose_name="Название рецепта."
    )
    image = models.ImageField(
        upload_to="recipes/",
        blank=True,
        verbose_name="Фото рецепта."
    )
    text = models.TextField(
        verbose_name="Подробное описание рецепта."
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Название ингредиента."
    )
    tag = models.ManyToManyField(
        Tag,
        verbose_name="Название тега."
    )
    cooking_time = models.PositiveBigIntegerField(
        verbose_name="Время приготовления."
    )
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Дата публикации."
    )

    class Meta:
        """Мета данные модели."""

        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-created",)

    def __str__(self) -> str:
        """Метод строкового представления модели."""

        return self.name
