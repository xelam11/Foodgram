from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ..users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name='Название',
                            help_text='Напишите название',
                            unique=True,
                            )
    color = models.CharField(max_length=7,
                             verbose_name='Код цвета',
                             help_text='Напишите код цвета',
                             default='#ffffff',
                             unique=True,
                             )
    slug = models.SlugField(max_length=100,
                            unique=True,
                            )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name='Название',
                            help_text='Напишите название'
                            )
    measurement_unit = models.CharField(max_length=100,
                                        verbose_name='Единица измерения',
                                        help_text='Укажите единицу измерения'
                                        )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag,
                                  related_name='recipe',
                                  verbose_name='Тег'
                                  )
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name='recipe',
                               verbose_name='Автор'
                               )
    ingredients = models.ManyToManyField(Ingredient,
                                         related_name='recipe',
                                         verbose_name='Ингредиент'
                                         )
    name = models.CharField(max_length=100,
                            verbose_name='Название',
                            help_text='Напишите название'
                            )
    image = models.ImageField(upload_to='media/',
                              verbose_name='Фото блюда',
                              help_text='Загрузите фото'
                              )
    text = models.TextField(verbose_name='Описание',
                            help_text='Напишите описание'
                            )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации'
                                    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        verbose_name='Время приготовления в минутах',
        help_text='Укажите время приготовления в минутах'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
