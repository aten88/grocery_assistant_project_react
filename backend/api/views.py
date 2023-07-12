from django.contrib.auth.models import User
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import RetrieveAPIView

from recipes.models import Tag, Ingredient, Recipe, Favorite
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    FavoriteSerializer, UserSerializer
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


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Recipe."""

    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class UserViewSet(viewsets.ViewSet):
    """Вьюсет модели User."""
    permission_classes = [AllowAny]

    def list(self, request):
        """Метод отображения списка пользователей."""
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Метод создания нового пользователя."""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            password = request.data.get('password')
            serializer.save(password=password)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(RetrieveAPIView):
    """Представление для User по id."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
