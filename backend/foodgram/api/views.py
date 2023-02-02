from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (AmountIngredient, Favorite, Follow, Ingredient,
                            Recipe, ShoppingCart, Tag)

from .pagination import CustomPaginations
from .permissions import IsOwner
from .serializers import (CustomTokenCreateSerializer,
                          FavoriteRecipeSerializer, FollowSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer, User, UserRegistrationSerializer,
                          UserSerializer, UserSetPasswordSerializer)


class TokenCreateViewSet(ObtainAuthToken):
    """Вьюсет для создания токена."""
    serializer_class = CustomTokenCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User,
                                 email=serializer.validated_data['email'])
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
        })


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для пользователей."""
    queryset = User.objects.all().order_by('id')
    pagination_class = CustomPaginations

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserRegistrationSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User(
                email=serializer.validated_data['email'],
                username=serializer.validated_data['username'],
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
            )
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response(self.get_serializer(user).data,
                            status=status.HTTP_201_CREATED)

    def get_permissions(self):
        if self.request.method == 'POST' and self.request.path in (
            '/api/users/', '/api/auth/token/login/'
        ):
            return (AllowAny(),)
        elif self.request.method == 'GET' and (
            self.request.path == '/api/users/'
        ):
            return (AllowAny(),)
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='me')
    def information_about_me(self, request):
        username = self.request.user
        user = get_object_or_404(User, username=username)
        if self.request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='set_password')
    def set_password(self, request, *args, **kwargs):
        serializer = UserSetPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if not self.request.user.check_password(
                serializer.data.get("current_password")
            ):
                return Response(
                    {"current_password": ["Введён некорректный пароль."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            self.request.user.set_password(serializer.data["new_password"])
            self.request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def follow(self, request, *args, **kwargs):
        serializer = FollowSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            following = get_object_or_404(
                    User,
                    id=self.kwargs.get('pk')
                )

            if request.method == 'POST':
                if self.request.user == following:
                    return Response(
                        {'Ошибка': ['Нельзя подписаться на самого себя!']},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                elif Follow.objects.filter(user=self.request.user,
                                           following=following).exists():
                    return Response(
                        {'Ошибка': ['Вы уже подписаны на пользователя!']},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                serializer.save(user=self.request.user, following=following)
                return Response(serializer.data)

            elif request.method == 'DELETE':
                if Follow.objects.filter(user=self.request.user,
                                         following=following).exists():
                    follow = get_object_or_404(
                        Follow,
                        user=self.request.user,
                        following=self.get_object()
                    )
                    follow.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                return Response(
                    {'Ошибка': ([f'Вы не подписаны на пользователя '
                                f'{following.username}!'])},
                    status=status.HTTP_400_BAD_REQUEST
                )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class IngredientVievSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    pagination_class = CustomPaginations
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        req = self.request
        queryset = Recipe.objects
        if not req.query_params:
            return queryset.all()
        if req.query_params.get('author'):
            queryset = queryset.filter(author=req.query_params['author'])
        if (req.query_params.get('is_favorited') == '1' and
                req.user.is_authenticated):
            queryset = queryset.filter(favorites__user=req.user)
        if (req.query_params.get('is_in_shopping_cart') == '1' and
                req.user.is_authenticated):
            queryset = queryset.filter(shopping_carts__user=req.user)
        if req.query_params.get('tags'):
            queryset = queryset.filter(tags__name=req.query_params['tags'])
        return queryset

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action in ('recipe_to_favorite',
                           'recipe_to_shopping_cart',
                           'download_shopping_cart'):
            return [IsAuthenticated(), IsOwner()]
        elif self.request.method in SAFE_METHODS:
            return [AllowAny()]
        elif self.request.method in ('PATCH', 'DELETE'):
            return [IsOwner()]
        return super().get_permissions()

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def recipe_to_favorite(self, request, *args, **kwargs):
        serializer = FavoriteRecipeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            recipe = get_object_or_404(
                    Recipe,
                    id=self.kwargs.get('pk')
                )

            if request.method == 'POST':
                if Favorite.objects.filter(user=self.request.user,
                                           recipe=recipe).exists():
                    return Response(
                        {'Ошибка': ['Рецепт уже добавлен в избранное!']},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                serializer.save(user=self.request.user, recipe=recipe)
                return Response(serializer.data, status=status.HTTP_200_OK)

            elif request.method == 'DELETE':
                if Favorite.objects.filter(user=self.request.user,
                                           recipe=recipe).exists():
                    recipe_in_favorite = Favorite.objects.get(
                        user=self.request.user,
                        recipe=recipe
                    )
                    recipe_in_favorite.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                return Response(
                    {'Ошибка': [f'Рецепт {recipe.name} '
                     f'отсутствует в списке избранных!']},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def recipe_to_shopping_cart(self, request, *args, **kwargs):
        serializer = ShoppingCartSerializer(data=request.data)
        user = self.request.user
        if serializer.is_valid(raise_exception=True):
            recipe = get_object_or_404(
                Recipe,
                id=self.kwargs.get('pk')
            )

            if request.method == 'POST':
                if ShoppingCart.objects.filter(recipe=recipe,
                                               user=user).exists():
                    return Response(
                        {'Ошибка': ['Рецепт уже добавлен в корзину!']},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                serializer.save(user=user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)

            if request.method == 'DELETE':
                if ShoppingCart.objects.filter(recipe=recipe,
                                               user=user).exists():
                    recipe_in_shopping_cart = ShoppingCart.objects.get(
                        recipe=recipe,
                        user=user
                    )
                    recipe_in_shopping_cart.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                return Response(
                    {'Ошибка': [f'Рецепт {recipe.name} '
                     f'отсутствует в корзине!']},
                    status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request, *args, **kwargs):
        ingredients_in_shopping_cart = AmountIngredient.objects.filter(
            recipe__shopping_carts__user=self.request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
                amount=Sum('amount'))

        text = ''
        for v in ingredients_in_shopping_cart:
            text += '\n'.join(
                [f"{v['ingredient__name']} - {v['amount']}"
                 f"{v['ingredient__measurement_unit']} " + "\n"])

        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename=shoping_cart.txt')
        return response


class FollowViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для подписок."""
    serializer_class = FollowSerializer
    pagination_class = CustomPaginations

    def get_queryset(self):
        req = self.request
        queryset = Follow.objects.filter(user=req.user)

        if 'recipes_limit' in req.query_params and int(
            req.query_params.get('recipes_limit')
        ) < 0:
            raise ValidationError(
                {"recipes_limit": ["Число должно быть больше или равно 0."]})
        return queryset
