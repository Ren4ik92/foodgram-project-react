from collections import OrderedDict

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from recipes.models import Recipe, Tag, Ingredient, IngredientAmount

User = get_user_model()


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


