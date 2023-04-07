from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import *
from recipes.models import Recipe, Tag, Ingredient, IngredientAmount


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
