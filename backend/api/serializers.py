from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.models import Ingredient, IngredientAmount, Recipe, Tag, Cart, Favorite
from users.models import Follow
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        write_only=True,
        source='ingredient'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount', 'ingredient')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientAmount.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


# class RecipeSerializer(serializers.ModelSerializer):
#     image = Base64ImageField()
#     tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
#     author = CustomUserSerializer(read_only=True)
#     ingredients = serializers.ListField(child=serializers.DictField())
#     is_favorited = serializers.SerializerMethodField()
#     is_in_shopping_cart = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Recipe
#         fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
#                   'is_in_shopping_cart', 'name', 'image', 'text',
#                   'cooking_time')
#
#     def get_is_favorited(self, obj):
#         user = self.context.get('request').user
#         if user.is_anonymous:
#             return False
#         return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()
#
#     def get_is_in_shopping_cart(self, obj):
#         user = self.context.get('request').user
#         if user.is_anonymous:
#             return False
#         return Recipe.objects.filter(cart__user=user, id=obj.id).exists()
#
#     def validate_ingredients(self, ingredients):
#         ingredients_list = []
#         if not ingredients:
#             raise serializers.ValidationError("Список ингредиентов не может быть пустым.")
#         for ingredient in ingredients:
#             if ingredient['id'] in ingredients_list:
#                 raise serializers.ValidationError(
#                     'Ингредиенты должны быть уникальны.')
#             ingredients_list.append(ingredient['id'])
#         return ingredients_list
#
#     def create_ingredients(self, ingredients, recipe):
#         ingredient_amounts = [
#             IngredientAmount(
#                 recipe=recipe,
#                 ingredient_id=ingredient.get('id'),
#                 amount=ingredient.get('amount')
#             )
#             for ingredient in ingredients
#         ]
#         IngredientAmount.objects.bulk_create(ingredient_amounts)
#
#     def create(self, validated_data):
#         ingredients_data = validated_data.pop('ingredients')
#         tags_data = validated_data.pop('tags')
#         recipe = Recipe.objects.create(**validated_data)
#         recipe.tags.set(tags_data)
#         self.create_ingredients(ingredients_data, recipe)
#
#         return recipe
#
#     def update(self, instance, validated_data):
#         ingredients_data = validated_data.pop('ingredients')
#         tags_data = validated_data.pop('tags')
#         instance.tags.clear()
#         instance.tags.set(tags_data)
#
#         IngredientAmount.objects.filter(recipe=instance).all().delete()
#         self.create_ingredients(ingredients_data, instance)
#
#         instance = super().update(instance, validated_data)
#
#         return instance
class ReadRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = Ingredient


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField()

    class Meta:
        fields = ('id', 'amount')
        model = Ingredient


class CreateRecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = CreateRecipeIngredientSerializer(
        many=True,
        write_only=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'author',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)

    def create(self, validated_data):
        current_user = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = validated_data.pop('author', current_user)
        recipe = Recipe.objects.create(author=author, **validated_data)
        ingredient_counts = {}
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            if ingredient_id in ingredient_counts:
                ingredient_counts[ingredient_id] += amount
            else:
                recipe_ingredient, created = (
                    Ingredient.objects.get_or_create(
                        recipe=recipe,
                        ingredient=ingredient_id,
                        defaults={'amount': amount},
                    )
                )
                if not created:
                    recipe_ingredient.amount += amount
                    recipe_ingredient.save()
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredient.clear()
        ingredient_counts = {}
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            if ingredient_id in ingredient_counts:
                ingredient_counts[ingredient_id] += amount
            else:
                ingredient_counts[ingredient_id] = amount
        create_ingredients = [
            Ingredient(
                recipe=instance,
                ingredient_id=ingredient_id,
                amount=amount
            )
            for ingredient_id, amount in ingredient_counts.items()
        ]
        Ingredient.objects.bulk_create(create_ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance, context=self.context).data

    def validate(self, data):
        if data.get('cooking_time') < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть не меньше одной минуты!')
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        if not ingredients or len(ingredients) == 0:
            raise serializers.ValidationError(
                'Рецепт должен содержать хотя бы один ингредиент!')
        if not tags or len(tags) == 0:
            raise serializers.ValidationError(
                'Рецепт должен содержать хотя бы один тег!')
        for ingredient in ingredients:
            if ingredient.get('amount') < 0:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть не меньше одного!')
        return data


class ReadRecipeSerializer(serializers.ModelSerializer):
    ingredients = ReadRecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True,
    )
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request:
            current_user = request.user
            if current_user.is_authenticated:
                return Favorite.objects.filter(
                    user=current_user, recipe=obj.id).exists()
            return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request:
            current_user = request.user
            if current_user.is_authenticated:
                return Cart.objects.filter(
                    user=current_user, recipe=obj.id).exists()
            return False

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'author',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )
        read_only_fields = (
            'id',
            'tags',
            'ingredients',
            'author',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )


class CropRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return CropRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
