from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import LIMIT_MODEL_FIELD


class CustomUser(AbstractUser):
    '''Модель кастомного юзера.'''

    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True
    )
    username = models.CharField(
        max_length=LIMIT_MODEL_FIELD,
        verbose_name='Имя пользователя',
        unique=True,
        db_index=True
    )
    first_name = models.CharField(
        max_length=LIMIT_MODEL_FIELD,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=LIMIT_MODEL_FIELD,
        verbose_name='Фамилия'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', ]

    class Meta:

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id', )

    def __str__(self) -> str:

        return self.username
