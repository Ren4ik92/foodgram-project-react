from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404
from rest_framework import serializers
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


class ReadRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientAmount


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        fields = ('id', 'amount',)
        model = IngredientAmount


#
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
        # ingredient_ids = set()
        # for ingredient in ingredients:
        #     ingredient_id = ingredient['id'].id
        #     if ingredient_id in ingredient_ids:
        #         raise serializers.ValidationError('Каждый ингредиент должен присутствовать только один раз')
        #     ingredient_ids.add(ingredient_id)

        ingredient_amounts = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id'].id
            amount = ingredient['amount']
            ingredient_amounts.append(
                IngredientAmount(
                    recipe=recipe,
                    ingredient_id=ingredient_id,
                    amount=amount
                )
            )
        IngredientAmount.objects.bulk_create(ingredient_amounts, ignore_conflicts=True)
        recipe.tags.set(tags)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe.tags.clear()
        recipe.tags.set(tags)
        recipe.ingredients.clear()
        create_ingredients = [
            IngredientAmount(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        ]
        IngredientAmount.objects.bulk_create(create_ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance, context=self.context).data

    def validate_tags(self, tags):
        if not tags or len(tags) == 0:
            raise serializers.ValidationError(
                'Рецепт должен содержать хотя бы один тег!')
        return tags

    def validate_ingredients(self, data):
        ingredients = data.get('ingredients')
        if not ingredients or len(ingredients) == 0:
            raise serializers.ValidationError(
                'Рецепт должен содержать хотя бы один ингредиент!')
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(Ingredient,
                                           id=ingredient_item['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError('Ингридиенты должны '
                                                  'быть уникальными')
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) < 0:
                raise serializers.ValidationError({
                    'ingredients': ('Убедитесь, что значение количества '
                                    'ингредиента больше 0')
                })
        data['ingredients'] = ingredients
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
