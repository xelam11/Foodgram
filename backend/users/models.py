from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=30, verbose_name='Имя',
                                  blank=True)
    last_name = models.CharField(max_length=30, verbose_name='Фамилия',
                                 blank=True)
    username = models.CharField(max_length=30, verbose_name='Юзернейм',
                                unique=True)
    email = models.EmailField(verbose_name='Электронная почта', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']


class Follow(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name="follower")
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                  related_name="following")

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'following'],
            name='%(app_label)s_%(class)s_unique_follow')]