from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('api/users/<int:id>/subscribe/', CustomUserViewSet.as_view({'post': 'subscribe'}), name='user-subscribe'),
    path('api/users/<int:id>/unsubscribe/', CustomUserViewSet.as_view({'delete': 'del_subscribe'}),
         name='user-unsubscribe'),
    path('api/users/subscriptions/', CustomUserViewSet.as_view({'get': 'subscriptions'}), name='user-subscriptions'),
]
