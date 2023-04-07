from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import TagViewSet, IngredientViewSet

router = DefaultRouter()
router.register('tags', TagViewSet, 'tags')
router.register('ingredients', IngredientViewSet, 'ingredients')
# router.register('recipes', RecipeViewSet, 'recipes')


urlpatterns = [
    path('v1/', include(router.urls)),
    # path('v1/', include('djoser.urls')),
    # path('v1/', include('djoser.urls.jwt')),
]
