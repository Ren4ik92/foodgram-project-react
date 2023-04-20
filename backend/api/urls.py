from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientsViewSet, RecipeViewSet, TagsViewSet

from users.views import CustomUserViewSet

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagsViewSet)
router.register('ingredients', IngredientsViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'users/<int:id>/subscribe/',
        CustomUserViewSet.as_view({'post': 'subscribe', 'delete': 'del_subscribe'}),
        name='subscribe'),
    path('recipes/<int:pk>/shopping_cart/',
         RecipeViewSet.as_view({'post': 'shopping_cart'}), name='recipe-shopping-cart'),
]
