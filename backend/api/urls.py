from django.urls import path, include
from rest_framework.routers import DefaultRouter
from djoser.views import TokenCreateView, TokenDestroyView

from .views import (
    TagViewSet, IngredientViewSet, RecipeViewSetList,
    AddFavoriteView, UserSubscriptionListAPIView
)
from .views import (
    UserViewSet, UserDetailView,
    CurrentUserViewSet, ChangePasswordViewSet)

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSetList)
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
        CurrentUserViewSet.as_view({'get': 'retrieve'}),
        name='current-user'
    ),
    path(
        'users/set_password/',
        ChangePasswordViewSet.as_view({'post': 'set_password'}),
        name='set-password'
    ),
    path('recipes/<int:id>/favorite/', AddFavoriteView.as_view()),
    path('', include(router.urls)),
]
