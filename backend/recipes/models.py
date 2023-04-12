from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import ForeignKey, UniqueConstraint, CASCADE,  DateTimeField

User = get_user_model()


class Recipe(models.Model):
    """Модель для рецептов.
        Основная модель приложения описывающая рецепты.
        """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='recipe_images/', null=True, blank=True)
    description = models.TextField()
    ingredients = models.ManyToManyField('Ingredient', through='IngredientAmount')
    tags = models.ManyToManyField('Tag')
    cooking_time = models.PositiveIntegerField()

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
    """Количество ингредиентов в блюде."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
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