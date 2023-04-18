from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('guest', 'Гость'),
        ('user', 'Авторизованный пользователь'),
        ('admin', 'Администратор')
    ]

    user_type = models.CharField(max_length=10,
                                 choices=USER_TYPE_CHOICES,
                                 default='guest')

    username = models.CharField(verbose_name='Уникальный юзернейм',
                                max_length=150, unique=True
                                )
    first_name = models.CharField(verbose_name='Имя',
                                  max_length=50
                                  )
    last_name = models.CharField(verbose_name='Фамилия',
                                 max_length=50)
    email = models.EmailField(verbose_name='Адрес электронной почты',
                              max_length=128,
                              unique=True
                              )
    password = models.CharField(verbose_name='Пароль',
                                max_length=128)
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='Группы',
        blank=True,
        help_text='Группы, к которым принадлежит этот пользователь.'
                  ' Пользователь получит все разрешения,'
                  ' предоставленные каждой из его групп.',
        related_name='myuser_set',  # add a custom related_name
        related_query_name='user'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='User permissions',
        blank=True,
        help_text='Определенные разрешения для этого пользователя.',
        related_name='myuser_set',  # add a custom related_name
        related_query_name='user'
    )

    def save(self, *args, **kwargs):
        if self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'


class Subscription(models.Model):
    user = models.ForeignKey(MyUser,
                             on_delete=models.CASCADE,
                             related_name='subscriptions')
    author = models.ForeignKey(MyUser,
                               on_delete=models.CASCADE,
                               related_name='subscribers')
    created_at = models.DateTimeField(auto_now_add=True)
