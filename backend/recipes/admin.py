from django.contrib import admin
from recipes.models import Recipe, Ingredient, IngredientAmount, Tag


class RecipeAmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'description', 'cooking_time')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount', 'unit')


admin.site.register(Recipe, RecipeAmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
