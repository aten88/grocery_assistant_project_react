from django.contrib.auth.models import User

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from recipes.models import Tag, Ingredient, Recipe, Favorite
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    FavoriteSerializer, UserSerializer
)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Recipe."""

    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class UserViewSet(viewsets.ViewSet):

    permission_classes = [AllowAny]

    def list(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
