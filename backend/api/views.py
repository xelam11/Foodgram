from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import IngredientFilter, RecipeFilter
from .models import (Favorite, Follow, Ingredient,
                     IngredientInRecipe, Recipe, ShoppingList, Tag)
from .paginators import PageNumberPaginatorModified
from .permissions import AdminOrAuthorOrReadOnly
from .serializers import (IngredientSerializer, TagSerializer, UserSerializer,
                          RecipeSerializer)
from users.models import CustomUser


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    filter_backends = [DjangoFilterBackend, ]
    filter_class = IngredientFilter
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, ]
    filter_class = RecipeFilter
    pagination_class = PageNumberPaginatorModified
    permission_classes = [AdminOrAuthorOrReadOnly, ]
    serializer_class = RecipeSerializer


class FollowViewSet(viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticated,)

    @action(detail=False)
    def subscriptions(self, request):
        user_qs = CustomUser.objects.filter(following__user=request.user)

        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(user_qs, request)
        serializer = UserSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['GET', 'DELETE'])
    def subscribe(self, request, **kwargs):
        user = request.user

        if request.method == 'GET':
            author = self.get_object()
            if Follow.objects.filter(user=user, author=author).exists():

                return Response({
                    'message': 'Вы уже подписаны',
                    'status': f'{status.HTTP_400_BAD_REQUEST}'
                })

            Follow.objects.create(user=user, author=author)

            return Response(status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            count, _ = Follow.objects.filter(
                author__pk=kwargs.get('pk'),
                user=user).delete()

            if count == 0:
                return Response(status=status.HTTP_404_NOT_FOUND)

            return Response({
                'message': 'Удалено',
                'status': f'{status.HTTP_204_NO_CONTENT}'
            })

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class FavouriteViewSet(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        _, is_created = Favorite.objects.get_or_create(user=user,
                                                       recipe=recipe)
        if not is_created:
            return Response({
                'message': 'Вы уже добавили рецепт в избранное',
                'status': f'{status.HTTP_400_BAD_REQUEST}'
            })

        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)

        count, _ = Favorite.objects.filter(
            recipe=recipe,
            user=user).delete()

        if count == 0:
            return Response({
                'message': 'Рецепт не был в избранном',
                'status': f'{status.HTTP_400_BAD_REQUEST}'
            })

        return Response({
            'message': 'Удалено',
            'status': f'{status.HTTP_204_NO_CONTENT}'
        })


class ShoppingListViewSet(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
            return Response({
                'message': 'Вы уже добавили рецепт в список покупок',
                'status': f'{status.HTTP_400_BAD_REQUEST}'
            })
        ShoppingList.objects.create(user=user, recipe=recipe)
        serializer = RecipeSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        shopping_list_obj = get_object_or_404(
            ShoppingList, user=user, recipe=recipe)
        if not shopping_list_obj:
            return Response({
                'message': 'Рецепт не был в списке покупок',
                'status': f'{status.HTTP_400_BAD_REQUEST}'
            })
        shopping_list_obj.delete()
        return Response({
            'message': 'Удалено',
            'status': f'{status.HTTP_204_NO_CONTENT}'
        })


class DownloadShoppingCart(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        shopping_cart = user.purchases.all()
        buying_list = {}
        for record in shopping_cart:
            recipe = record.recipe
            ingredients = IngredientInRecipe.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                amount = ingredient.amount
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                if name not in buying_list:
                    buying_list[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount
                    }
                else:
                    buying_list[name]['amount'] = (buying_list[name]['amount']
                                                   + amount)

        wishlist = []
        for item in buying_list:
            wishlist.append(f'{item} - {buying_list[item]["amount"]} '
                            f'{buying_list[item]["measurement_unit"]} \n')
        wishlist.append('\n')
        wishlist.append('FoodGram, 2021')
        response = HttpResponse(wishlist, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response
