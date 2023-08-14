from django.urls import path, include
from rest_framework.routers import DefaultRouter
from djoser.views import TokenCreateView, TokenDestroyView

from .views import (
    TagViewSet, IngredientViewSet, RecipeViewSet,
    AddFavoriteView, UserSubscriptionListAPIView,
    UserViewSet, UserDetailView, CurrentUserViewSet,
    ChangePasswordViewSet, AddToShoppingCart, DownloadShoppingCart
)

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'users', UserViewSet, basename='user')


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/token/login/', TokenCreateView.as_view(), name='token_create'),
    path(
        'auth/token/logout/', TokenDestroyView.as_view(), name='token_destroy'
    ),
    path(
        'users/subscriptions/', UserSubscriptionListAPIView.as_view(),
        name='user-subscriptions'
    ),
    path('users/<int:id>/', UserDetailView.as_view(), name='user-detail'),
    path(
        'users/me/',
        CurrentUserViewSet.as_view(),
        name='current-user'
    ),
    path(
        'users/set_password/',
        ChangePasswordViewSet.as_view({'post': 'set_password'}),
        name='set-password'
    ),
    path(
        'users/<int:id>/subscribe/',
        UserSubscriptionListAPIView.as_view(),
        name='subscribe-unsubscribe'
    ),
    path('recipes/<int:id>/favorite/', AddFavoriteView.as_view()),
    path('recipes/<int:id>/shopping_cart/', AddToShoppingCart.as_view()),
    path('recipes/download_shopping_cart/', DownloadShoppingCart.as_view(
        {'get': 'list'}
    )),
    path('', include(router.urls)),
]
