from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, Q


class User(AbstractUser):
    USER = 'user'
    MODER = 'moderator'
    ADMIN = 'admin'

    ROLES = (
        (USER, 'User'),
        (MODER, 'Moderator'),
        (ADMIN, 'Administrator'),
    )

    username = models.CharField(
        'username',
        max_length=200,
        unique=True,
        db_index=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        unique=False,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        unique=False,
        blank=True,
        null=True
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    password = models.CharField(
        max_length=250,
        unique=False,
        blank=True,
        null=True
    )
    bio = models.TextField(
        'Биография',
        blank=True,
        null=True
    )
    role = models.CharField(
        'Роль',
        max_length=21,
        choices=ROLES,
        blank=True,
        default='user'
    )

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        constraints = [
            CheckConstraint(check=~Q(username='me'), name='name_not_me')
        ]

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moder(self):
        return self.role == self.MODER

    @property
    def is_user(self):
        return self.role == self.USER
