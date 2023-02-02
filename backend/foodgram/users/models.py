from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        help_text=('До 150 символов, состоящих из: @/./+/-/_'),
        validators=[username_validator],
        error_messages={
            'unique': ("Пользователь с таким именем уже существует."),
        },
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    password = models.CharField('Пароль', max_length=150)
    email = models.EmailField('email', max_length=254)

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username
