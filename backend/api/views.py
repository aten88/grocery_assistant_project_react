from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from recipes.models import Tag, Ingredient, Recipe, Favorite
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer
)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]


class RecipeViewSetList(viewsets.ModelViewSet):
    """Вьюсет списка модели Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny]


class AddFavoriteView(APIView):
    """Вьюсет добавления рецепта."""

    def post(self, request, id):
        """"Метод добавления рецепта в избранное."""
        try:
            recipe = Recipe.objects.get(id=id)
        except Recipe.DoesNotExist:
            return Response(
                'Рецепт не найден',
                status=status.HTTP_404_NOT_FOUND
            )
        if Favorite.objects.filter(user=request.user, recipe=recipe):
            return Response(
                'Рецепт уже в избранном',
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite(user=request.user, recipe=recipe).save()
        return Response(
            'Рецепт успешно добавлен в избранное',
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, id):
        """Метод удаления рецепта из избранного"""
        try:
            favorite = Favorite.objects.get(user=request.user, recipe_id=id)
            favorite.delete()
        except Favorite.DoesNotExist:
            return Response(
                'Рецепт не найден в избранном',
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            'Рецепт успешно удален из избранного',
            status=status.HTTP_204_NO_CONTENT
        )
