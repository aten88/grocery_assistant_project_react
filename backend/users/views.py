from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import RetrieveAPIView

from users.serializers import UserSerializer


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
    """Представление для User по id."""

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
