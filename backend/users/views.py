from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import RecipeSerializer
from models import MyUser, Subscription
from recipes.models import Recipe


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe(request, author_id):
    author = MyUser.objects.get(id=author_id)
    subscription, created = Subscription.objects.get_or_create(user=request.user, author=author)
    if created:
        return Response({'success': True, 'message': f'Вы успешно подписались на {author.username}'})
    else:
        return Response({'success': False, 'message': f'Вы уже подписаны на {author.username}'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unsubscribe(request, author_id):
    author = MyUser.objects.get(id=author_id)
    Subscription.objects.filter(user=request.user, author=author).delete()
    return Response({'success': True, 'message': f'Вы успешно отписались от {author.username}'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_subscriptions(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    authors = [subscription.author for subscription in subscriptions]
    recipes = Recipe.objects.filter(author__in=authors).order_by('-created_at')
    serializer = RecipeSerializer(recipes, many=True)
    return Response(serializer.data)
