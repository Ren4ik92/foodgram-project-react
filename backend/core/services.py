"""Модуль вспомогательных функций.
"""
from typing import TYPE_CHECKING
from rest_framework import serializers

from recipes.models import AmountIngredient, Recipe


if TYPE_CHECKING:
    from recipes.models import Ingredient


def recipe_amount_ingredients_set(
    recipe: Recipe,
    ingredients: dict[int, tuple['Ingredient', int]]
) -> None:

    objs = []

    for ingredient, amount in ingredients.values():
        if amount > 10001:
            raise serializers.ValidationError('Неправильное количество ингидиента')
        if amount <= 0:
            raise serializers.ValidationError('Колличество ингридиентов должно быть больше нуля')
        objs.append(AmountIngredient(
            recipe=recipe,
            ingredients=ingredient,
            amount=amount
        ))

    AmountIngredient.objects.bulk_create(objs)


incorrect_layout = str.maketrans(
    'qwertyuiop[]asdfghjkl;\'zxcvbnm,./',
    'йцукенгшщзхъфывапролджэячсмитьбю.'
)
