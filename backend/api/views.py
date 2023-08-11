from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.generics import (
    RetrieveAPIView, ListAPIView, get_object_or_404
)
from rest_framework.pagination import PageNumberPagination

from recipes.models import (
    Tag, Ingredient, Recipe, Favorite,
    Subscription, ShoppingCart
)
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    SubscriptionSerialiazer, FavoriteSerializer,
    ShoppingCartSerializer, UserSerializer, UserDetailSerializer,
    RecipeSerializerDetail, SubscriptionCreateSerializer,
)
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .filters import IngredientFilter, RecipeFilter
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
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter


class RecipeViewSetDetail(viewsets.ModelViewSet):
    '''Вьюсет модели Recipe по id.'''

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializerDetail
    permission_classes = [IsAuthorOrReadOnly]
    lookup_field = 'id'
    pagination_class = None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('id')
        return context

    def partial_update(self, request, *args, **kwargs):
        '''Метод обновления данных в рецептe по id.'''
        instance = self.get_object()
        serializer = RecipeSerializer(
            instance, data=request.data, partial=True
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

        if recipe.author == request.user:
            return Response(
                'Вы не можете добавить свой рецепт в избранное.',
                status=status.HTTP_400_BAD_REQUEST
            )
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            return Response(
                'Данный рецепт уже добавлен в избранное',
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite_data = {'user': request.user.id, 'recipe': recipe.id}
        serializer = FavoriteSerializer(data=favorite_data)
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
        user = request.user
        if ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            return Response(
                'Рецепт уже добавлен в список покупок.',
                status=status.HTTP_400_BAD_REQUEST
            )
        cart_data = {'user': user.id, 'recipe': recipe.id}
        serializer = ShoppingCartSerializer(data=cart_data)
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
    queryset = User.objects.order_by('-date_joined').all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination

    def create(self, request):
        '''Метод создания нового пользователя.'''
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            password = request.data.get('password')
            serializer.save(password=make_password(password))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(RetrieveAPIView):
    '''Вьюсет для User по id.'''

    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = 'id'


class CurrentUserViewSet(RetrieveAPIView):
    '''API view для получения данных текущего пользователя.'''
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        '''Метод для получения текущего пользователя.'''
        return self.request.user


class ChangePasswordViewSet(viewsets.ViewSet):
    '''Вьюсет для смены пароля.'''

    permission_classes = [IsAuthenticated]

    def set_password(self, request):
        '''Метод проверки и смены пароля.'''
        user = request.user
        new_password = request.data.get('new_password')
        current_password = request.data.get('current_password')

        if not (
            user.check_password(current_password)
            and current_password != new_password and new_password is not None
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
            data={'id': id}, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        response_data = serializer.save()

        return Response(response_data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        '''Метод удаления подписки по id.'''
        user_to_unsubscribe = get_object_or_404(User, id=id)

        if get_object_or_404(
            Subscription, user=request.user, author=user_to_unsubscribe
        ):
            get_object_or_404(
                Subscription, user=request.user, author=user_to_unsubscribe
            ).delete()
            return Response(
                'Вы отписались от автора.', status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            'Подписки не существует', status=status.HTTP_204_NO_CONTENT
        )
