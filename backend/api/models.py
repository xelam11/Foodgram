from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.html import format_html

from users.models import CustomUser


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Пользователь подписчик',
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Пользователь на которого подписываемся',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_follow')]

    def __str__(self):
        return f'{self.user} => {self.author}'


class Tag(models.Model):
    name = models.CharField(max_length=200,
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
    slug = models.SlugField(max_length=200,
                            unique=True,
                            )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

    def colored_name(self):
        return format_html(
            '<span style="color: #{};">{}</span>',
            self.hex_color,)


class Ingredient(models.Model):
    name = models.CharField(max_length=200,
                            unique=True,
                            verbose_name='Название',
                            help_text='Напишите название',
                            )
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Единица измерения',
                                        help_text='Укажите единицу измерения',
                                        )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag,
                                  related_name='recipes',
                                  blank=True,
                                  verbose_name='Тег',
                                  )
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор',
                               )
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientInRecipe',
                                         related_name='recipes',
                                         verbose_name='Ингредиент',
                                         )
    name = models.CharField(max_length=200,
                            verbose_name='Название',
                            help_text='Напишите название',
                            )
    image = models.ImageField(upload_to='recipes',
                              verbose_name='Фото блюда',
                              help_text='Загрузите фото',
                              )
    text = models.TextField(verbose_name='Описание',
                            help_text='Напишите описание',
                            )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации',
                                    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        verbose_name='Время приготовления в минутах',
        help_text='Укажите время приготовления в минутах',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ингредиент в рецепте',
                                   )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов',
        default=1,
        validators=[MinValueValidator(1), ]
    )


class Favorite(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='favorite_subscriber',
                             verbose_name='Пользователь',
                             )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorite_recipe',
                               verbose_name='Рецепт',
                               )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата добавления',
                                    )

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorites_recipes')]

    def __str__(self):
        return (f'Пользователь: {self.user}, '
                f'избранные рецепты: {self.recipe.name}')


class ShoppingList(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='purchases',
                             verbose_name='Пользователь',
                             )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='customers',
                               verbose_name='Покупка',
                               )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата добавления',
                                    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'Пользователь: {self.user}, покупает:{self.recipe}'
