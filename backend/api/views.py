from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, get_object_or_404
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser
from recipes.models import (
    Favorite, Ingredient, Recipe, ShoppingCart, Subscription, Tag
)
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .serializers import (
    ChangePasswordSerializer, FavoriteSerializer, IngredientSerializer,
    RecipeReadSerializer, RecipeWriteSerializer, ShoppingCartSerializer,
    SubscriptionCreateSerializer, SubscriptionSerialiazer, TagSerializer,
    UserSerializer
)
from .utils import gen_shopping_list


class TagViewSet(viewsets.ModelViewSet):
    '''Вьюсет модели Tag.'''

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    '''Вьюсет модели Ingredient.'''

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    '''Вьюсет списка модели Recipe.'''

    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def create(self, request, *args, **kwargs):
        '''Метод создания нового рецепта.'''
        serializer = RecipeWriteSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        '''Метод обновления данных в рецептe по id.'''
        instance = self.get_object()
        serializer = RecipeWriteSerializer(
            instance, data=request.data, context={'request': request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        '''Метод удаления рецепта по id.'''
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddFavoriteView(APIView):
    '''Вьюсет добавления рецепта.'''

    def post(self, request, id):
        '''Метод добавления рецепта в избранное.'''
        recipe = get_object_or_404(Recipe, id=id)
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        '''Метод удаления рецепта из избранного.'''
        get_object_or_404(Favorite, user=request.user, recipe_id=id).delete()
        return Response(
            'Рецепт успешно удален из избранного',
            status=status.HTTP_204_NO_CONTENT
        )


class AddToShoppingCart(APIView):
    '''Вьюсет для добавления рецепта в список покупок.'''

    def post(self, request, id):
        '''Метод для добавления рецепта в список покупок.'''
        recipe = get_object_or_404(Recipe, id=id)
        serializer = ShoppingCartSerializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        '''Метод удаления рецепта из списка покупок.'''
        get_object_or_404(
            ShoppingCart, user=request.user, recipe_id=id
        ).delete()
        return Response(
            'Рецепт удален из списка покупок.',
            status=status.HTTP_204_NO_CONTENT
        )


class DownloadShoppingCart(viewsets.ViewSet):
    '''Вьюсет загрузки списка покупок.'''

    permission_classes = [IsAuthenticated]

    def list(self, request):
        '''Метод для обработки Get запросов.'''

        ingredients = gen_shopping_list(request.user)

        file_content = '\n'.join(
            [f'{ingredient} — {amount}'
             for ingredient, amount in ingredients.items()]
        )

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        response.write(file_content)
        return response


class UserViewSet(viewsets.ModelViewSet):
    '''Вьюсет модели User.'''
    queryset = CustomUser.objects.order_by('-date_joined').all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination

    def create(self, request):
        '''Метод создания нового пользователя.'''
        serializer = UserSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            password = request.data.get('password')
            serializer.save(password=make_password(password))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(RetrieveAPIView):
    '''Вьюсет для User по id.'''

    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'


class CurrentUserViewSet(RetrieveAPIView):
    '''API view для получения данных текущего пользователя.'''
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        '''Метод для получения текущего пользователя.'''
        return self.request.user


class ChangePasswordViewSet(viewsets.ViewSet):
    '''Вьюсет для смены пароля.'''

    permission_classes = [IsAuthenticated]

    def set_password(self, request):
        '''Метод проверки и смены пароля.'''
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )

        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)

            return Response(
                {'detail': 'Пароль успешно изменен'},
                status=status.HTTP_204_NO_CONTENT
            )


class UserSubscriptionListAPIView(ListAPIView):
    '''Вьюсет для получения списка подписок.'''

    serializer_class = SubscriptionSerialiazer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        '''Метод получения подписок юзера.'''
        return self.request.user.follower.all()

    def post(self, request, id):
        '''Метод создания подписки по id.'''
        serializer = SubscriptionCreateSerializer(
            data={'user': request.user.id, 'author': id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        '''Метод удаления подписки по id.'''
        subscription = get_object_or_404(
            Subscription, user=request.user, author_id=id
        )
        subscription.delete()
        return Response(
            'Подписки не существует', status=status.HTTP_204_NO_CONTENT
        )
