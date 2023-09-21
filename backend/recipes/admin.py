from django import forms
from django.contrib import admin

from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Subscription, Tag
)
from recipes.constants import LIMIT_INLINE_VALUE


class TagAdminForm(forms.ModelForm):
    '''Форма валидации модели Tag.'''
    class Meta:
        model = Tag
        fields = ['name', 'color', 'slug']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        color = cleaned_data.get('color')
        slug = cleaned_data.get('slug')

        if Tag.objects.filter(name=name).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Ошибка валидации.')

        if Tag.objects.filter(color=color).exclude(
            id=self.instance.id
        ).exists():
            raise forms.ValidationError('Ошибка валидации.')

        if Tag.objects.filter(slug=slug).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Ошибка валидации.')

        return cleaned_data


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    form = TagAdminForm


class IngredientAdminForm(forms.ModelForm):
    '''Форма валидации модели Ingredient.'''
    class Meta:
        model = Ingredient
        fields = ['name', 'measurement_unit', ]

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if Ingredient.objects.filter(name=name).exclude(
            id=self.instance.id
        ).exists():
            raise forms.ValidationError(
                'Ингредиент с таким названием уже существует.'
            )

        return cleaned_data


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    form = IngredientAdminForm


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = LIMIT_INLINE_VALUE
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    '''Форма валидации модели Favorite.'''
    def save_model(self, request, obj, form, change):
        user = request.user
        recipe = obj.recipe

        if user == recipe.author:
            raise forms.ValidationError(
                'Вы не можете добавить свой рецепт в избранное.'
            )

        if recipe.favorites.filter(user=user).exists():
            raise forms.ValidationError(
                'Данный рецепт уже добавлен в избранное.'
            )
        obj.user = user
        obj.save()


class SubscriptionAdminForm(forms.ModelForm):
    '''Форма валидации модели Subscription.'''
    class Meta:
        model = Subscription
        fields = ['author', 'user', ]

    def clean(self):
        cleaned_data = super().clean()
        author = cleaned_data.get('author')
        user = cleaned_data.get('user')

        if author == user:
            raise forms.ValidationError(
                'Ошибка валидации. Вы не можете подписаться на себя.'
            )

        if author.follow.filter(user=user).exclude(
            id=self.instance.id
        ).exists():
            raise forms.ValidationError('Ошибка валидации.')

        return cleaned_data


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    form = SubscriptionAdminForm


class ShoppingCartAdminForm(forms.ModelForm):
    '''Форма валидации модели ShoppingCart.'''
    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe', ]

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        recipe = cleaned_data.get('recipe')

        if user.shopping_user.filter(recipe=recipe).exclude(
            id=self.instance.id
        ).exists():
            raise forms.ValidationError('Ошибка валидации.')

        return cleaned_data


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    form = ShoppingCartAdminForm


class RecipeIngredientAdminForm(forms.ModelForm):
    '''Форма валидации модели RecipeIngredient.'''
    class Meta:
        model = RecipeIngredient
        fields = ['recipe', 'ingredient', 'amount', ]

    def clean(self):
        cleaned_data = super().clean()
        recipe = cleaned_data.get('recipe')
        ingredient = cleaned_data.get('ingredient')

        if recipe.recipe_ingredients_set.filter(ingredient=ingredient).exclude(
            id=self.instance.id
        ).exists():
            raise forms.ValidationError('Ошибка валидации.')

        return cleaned_data


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    form = RecipeIngredientAdminForm
