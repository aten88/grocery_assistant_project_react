from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
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
