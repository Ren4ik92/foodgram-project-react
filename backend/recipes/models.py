from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import ForeignKey, UniqueConstraint, CASCADE, DateTimeField, SET_NULL

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название блюда',
        max_length=60,
        default=''
    )
    author = ForeignKey(
        verbose_name='Автор рецепта',
        related_name='recipes',
        to=User,
        on_delete=SET_NULL,
        null=True,
    )
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='recipe_images/', null=True, blank=True)
    description = models.TextField()
    ingredients = models.ManyToManyField('Ingredient', through='IngredientAmount', related_name='recipes')
    tags = models.ManyToManyField('Tag')
    text = models.TextField(
        verbose_name='Описание блюда',
        max_length=200,
        default=''
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Tag(models.Model):
    """Тэги для рецептов."""

    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    """Ингридиенты для рецепта."""

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class IngredientAmount(models.Model):
    recipe = ForeignKey(
        verbose_name='В каких рецептах',
        related_name='ingredient_amounts',
        to=Recipe,
        on_delete=CASCADE,
    )
    ingredient = ForeignKey(
        verbose_name='Связанные ингредиенты',
        related_name='ingredient_amounts',
        to=Ingredient,
        on_delete=CASCADE,
    )
    amount = models.FloatField()
    unit = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.amount} {self.unit} of {self.ingredient.name}'

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингредиентов'


class Favorites(models.Model):
    """Избранные рецепты.
    Модель связывает Recipe и  User.
    """
    recipe = ForeignKey(
        verbose_name='Понравившиеся рецепты',
        related_name='in_favorites',
        to=Recipe,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name='Пользователь',
        related_name='favorites',
        to=User,
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'user',),
                name='\n%(app_label)s_%(class)s recipe is favorite alredy\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'


class Carts(models.Model):
    """Рецепты в корзине покупок.
    Модель связывает Recipe и  User.
    """
    recipe = ForeignKey(
        verbose_name='Рецепты в списке покупок',
        related_name='in_carts',
        to=Recipe,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name='Владелец списка',
        related_name='carts',
        to=User,
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'user',),
                name='\n%(app_label)s_%(class)s recipe is cart alredy\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'
