from urllib.parse import unquote

from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .mixins import AddDelViewMixin
from djoser.views import UserViewSet as DjoserUserViewSet
from .paginators import PageLimitPagination
from .serializers import *
from recipes.models import Recipe, Tag, Ingredient, IngredientAmount
from users.models import Subscription
from .permissions import *
from core.enums import UrlQueries, Tuples


class UserViewSet(DjoserUserViewSet, AddDelViewMixin):
    """Для авторизованных пользователей —
    возможность подписаться на автора рецепта.
    """
    pagination_class = PageLimitPagination
    add_serializer = UserSubscribeSerializer
    permission_classes = (DjangoModelPermissions,)

    @action(
        methods=Tuples.ACTION_METHODS,
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request: WSGIRequest, id: int | str):
        return self._add_del_obj(id, Subscription, Q(author__id=id))

    @action(methods=('get',), detail=False)
    def subscriptions(self, request: WSGIRequest):
        if self.request.user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)

        pages = self.paginate_queryset(
            User.objects.filter(subscribers__user=self.request.user)
        )
        serializer = UserSubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Работает с тэгами.
    Изменение и создание тэгов разрешено только админам.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Работет с игридиентами.
    Изменение и создание ингридиентов разрешено только админам.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)

    def get_queryset(self):

        name: str = self.request.query_params.get(UrlQueries.SEARCH_ING_NAME)
        queryset = self.queryset

        if name:
            if name[0] == '%':
                name = unquote(name)
            else:
                name = name.translate()

            name = name.lower()
            start_queryset = list(queryset.filter(name__istartswith=name))
            ingridients_set = set(start_queryset)
            cont_queryset = queryset.filter(name__icontains=name)
            start_queryset.extend(
                [ing for ing in cont_queryset if ing not in ingridients_set]
            )
            queryset = start_queryset

        return queryset
