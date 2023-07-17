from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination

from recipes.models import (
    Tag, Ingredient, Recipe,
    Favorite, Subscription, ShoppingCart
)
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    SubscriptionSerialiazer, FavoriteRecipeSerializer, ShoppingCartSerializer
)
from .serializers import UserSerializer


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
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


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
        if recipe.author == request.user:
            return Response(
                'Вы не можете добавить свой рецепт в избранное.'
            )
        if Favorite.objects.filter(user=request.user, recipe=recipe):
            return Response(
                'Рецепт уже в избранном',
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite(user=request.user, recipe=recipe).save()
        serializer = FavoriteRecipeSerializer(recipe)
        return Response(
            serializer.data,
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


class AddToShoppingCart(APIView):
    """Вьюсет для добавления рецепта в список покупок."""

    def post(self, request, id):
        """Метод для добавления рецепта в список покупок."""
        try:
            recipe = Recipe.objects.get(id=id)
            user = request.user
        except Recipe.DoesNotExist:
            return Response(
                'Рецепт не найден.',
                status=status.HTTP_404_NOT_FOUND
            )
        if ShoppingCart.objects.filter(user=request.user, recipe=recipe):
            return Response(
                'Рецепт уже добавлен в список покупок.',
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart(user=user, recipe=recipe).save()
        serializer = ShoppingCartSerializer(
            ShoppingCart(user=user, recipe=recipe)
        )
        serializer = FavoriteRecipeSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, id):
        """Метод удаления рецепта из списка покупок."""
        try:
            ShoppingCart.objects.get(user=request.user, recipe_id=id).delete()
        except ShoppingCart.DoesNotExist:
            return Response(
                'Рецепт не добавлен в список покупок.',
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            'Рецепт удален из списка покупок.',
            status=status.HTTP_204_NO_CONTENT
        )


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
            serializer.save(password=make_password(password))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(RetrieveAPIView):
    """Вьюсет для User по id."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'


class CurrentUserViewSet(viewsets.ViewSet):
    """Вьюсет для получения текущего пользователя."""

    permission_classes = [IsAuthenticated]

    def retrieve(self, request):
        """Метод получения данных текущего пользователя."""

        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class ChangePasswordViewSet(viewsets.ViewSet):
    """Вьюсет для смены пароля."""

    permission_classes = [IsAuthenticated]

    def set_password(self, request):
        """Метод проверки и смены пароля."""
        user = request.user
        new_password = request.data.get('new_password')
        current_password = request.data.get('current_password')

        if not (
            user.check_password(current_password) and
            current_password != new_password and
            new_password is not None
        ):
            return Response(
                {'detail': 'Неверный пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()

        return Response(
            {'detail': 'Пароль успешно изменен'},
            status=status.HTTP_204_NO_CONTENT
        )


class UserSubscriptionListAPIView(ListAPIView):
    """Вьюсет для получения списка подписок."""

    serializer_class = SubscriptionSerialiazer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """Метод получения подписок юзера."""
        return Subscription.objects.filter(user=self.request.user)
