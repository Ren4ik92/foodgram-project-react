from collections import OrderedDict
from django.contrib.auth import get_user_model
from django.db.models import QuerySet, F
from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from recipes.models import Recipe, Tag, Ingredient, IngredientAmount

User = get_user_model()


class ShortRecipeSerializer(ModelSerializer):
    """Укороченный Сериализатор для модели Recipe.
    """

    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = '__all__',


class UserSerializer(ModelSerializer):
    """Сериализатор для использования с моделью User.
    """
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = 'is_subscribed',

    def get_is_subscribed(self, obj: User) -> bool:
        user = self.context.get('view').request.user

        if user.is_anonymous or (user == obj):
            return False

        return user.subscriptions.filter(author=obj).exists()

    def create(self, validated_data: dict) -> User:
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSubscribeSerializer(UserSerializer):
    """Сериализатор вывода авторов на которых подписан текущий пользователь.
    """
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = '__all__',

    def get_is_subscribed(*args) -> bool:
        return True

    def get_recipes_count(self, obj: User) -> int:
        return obj.recipes.count()


class TagSerializer(ModelSerializer):
    """Сериализатор для вывода тэгов.
    """

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__',

    def validate(self, data: OrderedDict):
        for attr, value in data.items():
            data[attr] = value.sttrip(' #').upper()

        return data


class IngredientSerializer(ModelSerializer):
    """Сериализатор для вывода ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__',


class RecipeSerializer(ModelSerializer):
    """Сериализатор для рецептов.
    """
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
        )

    def get_ingredients(self, recipe: Recipe) -> QuerySet[dict]:
        return recipe.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount'))

    def get_is_favorited(self, recipe: Recipe) -> bool:
        user = self.context.get('view').request.user

        if user.is_anonymous:
            return False

        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:

        user = self.context.get('view').request.user

        if user.is_anonymous:
            return False

        return user.carts.filter(recipe=recipe).exists()

    @atomic
    def create(self, validated_data: dict) -> Recipe:

        tags: list[int] = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        return recipe

    @atomic
    def update(self, recipe: Recipe, validated_data: dict):

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            recipe.ingredients.set(ingredients)

        recipe.save()
        return recipe
