from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    TagViewSet, IngredientViewSet, RecipeViewSet,
    FavoriteViewSet, UserViewSet, UserDetailView
)

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'favorite', FavoriteViewSet)
router.register(r'users', UserViewSet, basename='user')


urlpatterns = [
    path('auth/token/login/', obtain_auth_token, name='api_token_auth'),
    path('users/<int:id>/', UserDetailView.as_view(), name='user-detail'),
    path('', include(router.urls)),
]
