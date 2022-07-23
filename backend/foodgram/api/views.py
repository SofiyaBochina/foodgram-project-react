import datetime as dt
import os
from wsgiref.util import FileWrapper

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag)

from .filters import IngredientFilter, UserRecipeFilter
from .permissions import IsAuthorAdminOrReadOnly, ReadOnly
from .serializers import (IngredientSerializer, MyUserSerializer,
                          RecipeSerializer, RecipeSerializerGet, RecipeUser,
                          SubscriptionSerializer, TagSerializer)

User = get_user_model()


class MyUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    pagination_class = LimitOffsetPagination

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(
            User,
            id=self.kwargs.get('id')
        )
        if user == author:
            return Response(
                'Подписка самого на себя запрещена!',
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'POST':
            subscription = Subscription.objects.create(
                user=user,
                author=author
            )
            serializer = SubscriptionSerializer(
                subscription.author,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        Subscription.objects.filter(
            user=user,
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(IsAuthenticated,),
        serializer_class=MyUserSerializer
    )
    def subscriptions(self, request):
        user = request.user
        user = get_object_or_404(
            User,
            id=user.id
        )
        queryset = [i.author for i in user.subscriber.all()]
        serializer = SubscriptionSerializer(
            queryset,
            many=True,
            context={'request': request},
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_class = UserRecipeFilter
    permission_classes = (IsAuthorAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializerGet
        return RecipeSerializer

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='favorite',
        url_name='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs.get('pk')
        )
        if request.method == 'POST':
            favorite = Favorite.objects.create(
                user=user,
                recipes=recipe
            )
            serializer = RecipeUser(
                favorite.recipes,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        Favorite.objects.filter(
            user=user,
            recipes=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs.get('pk')
        )
        if request.method == 'POST':
            cart = ShoppingCart.objects.create(
                user=user,
                recipes=recipe
            )
            serializer = RecipeUser(
                cart.recipes,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        ShoppingCart.objects.filter(
            user=user,
            recipes=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        f_data = []
        for i, ingredient in enumerate(shopping_cart, 1):
            f_data.append(
                '{}) {} {} {};'.format(
                    i,
                    ingredient['ingredient__name'],
                    ingredient['amount'],
                    ingredient["ingredient__measurement_unit"]
                )
            )
        f_text = '\n'.join(f_data)
        basename = "shopping_cart"
        suffix = dt.datetime.now().strftime("%y%m%d_%H%M%S")
        f_name = "_".join([basename, suffix])
        f = open(f'{f_name}.txt', 'a')
        f.write(f_text)
        f.close()
        f = open(f'{f_name}.txt', 'r')
        response = HttpResponse(
            FileWrapper(f),
            content_type='application/msword'
        )
        response['Content-Disposition'] = (
            'attachment; '
            f'filename="{f_name}.txt"'
        )
        os.remove(f'{f_name}.txt')
        return response

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (ReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (ReadOnly,)
    filter_class = IngredientFilter
