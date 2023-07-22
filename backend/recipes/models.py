from django.db import models
from django.contrib.auth.models import User


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
        decimal_places=2,
        verbose_name="Количество ингредиента."
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name="Единица измерения."
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
        verbose_name="Название рецепта.",
        unique=True
    )
    image = models.ImageField(
        upload_to="recipes/",
        blank=True,
        null=True,
        verbose_name="Фото рецепта."
    )
    text = models.TextField(
        verbose_name="Подробное описание рецепта."
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Название ингредиента."
    )
    tags = models.ManyToManyField(
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


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="Favorites"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="Favorites"
    )

    class Meta:
        """Мета=данные модели."""

        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"

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
        """Мета данные модели."""

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        """Метод строкового представления модели."""
        return (
            f'Пользователь {self.user} подписан на {self.author}'
        )


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
        """Мета данные модели."""

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self) -> str:
        """Метод строкового представления модели."""
        return f'{self.recipe} добавлен в список покупок {self.user}'
