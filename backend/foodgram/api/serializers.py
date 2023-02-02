from django.contrib.auth import get_user_model
from django.db import transaction
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (AmountIngredient, Favorite, Follow, Ingredient,
                            Recipe, ShoppingCart, Tag)
# from users.models import User

User = get_user_model()


class CustomTokenCreateSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""
    password = serializers.CharField(
        label="Password",
        max_length=150,
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    email = serializers.CharField(
        label="Email",
        max_length=254,
        style={'input_type': 'email'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label="Token",
        read_only=True
    )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password',
                  'is_subscribed')
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user.id
        queryset = Follow.objects.filter(following=obj.id,
                                         user=request_user).exists()
        return queryset


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации нового пользователя."""

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password')
        extra_kwargs = {'password': {'write_only': True}}


class UserSetPasswordSerializer(serializers.Serializer):
    """Сериализатор изменения пароля пользователя."""
    new_password = serializers.CharField(max_length=150, required=True)
    current_password = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ('new_password', 'current_password')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AmountIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор кол-ва ингредиентов."""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    tags = TagSerializer(many=True)
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = AmountIngredientSerializer(many=True,
                                             source='amountingredient_set')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        request_user = self.context.get('request').user.id
        queryset = Favorite.objects.filter(recipe=obj.id,
                                           user=request_user).exists()
        return queryset

    def get_is_in_shopping_cart(self, obj):
        request_user = self.context.get('request').user.id
        queryset = ShoppingCart.objects.filter(recipe=obj.id,
                                               user=request_user).exists()
        return queryset


class TagCreateInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для выбора тэгов при создании рецепта."""
    name = serializers.StringRelatedField()
    color = serializers.ReadOnlyField()
    slug = serializers.ReadOnlyField()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientCreateInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для выбора ингредиентов при создании рецепта."""
    id = serializers.PrimaryKeyRelatedField(source='ingredient',
                                            queryset=Ingredient.objects.all())
    name = serializers.StringRelatedField(source='ingredient')
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования рецептов."""
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all(),
                                              required=True)
    author = UserSerializer(read_only=True, required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = IngredientCreateInRecipeSerializer(
        many=True,
        source='amountingredient_set',
        required=True
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        extra_kwargs = {'name': {'required': True},
                        'text': {'required': True},
                        'cooking_time': {'required': True}}

    def get_is_favorited(self, obj):
        request_user = self.context.get('request').user.id
        queryset = Favorite.objects.filter(recipe=obj.id,
                                           user=request_user).exists()
        return queryset

    def get_is_in_shopping_cart(self, obj):
        request_user = self.context.get('request').user.id
        queryset = ShoppingCart.objects.filter(recipe=obj.id,
                                               user=request_user).exists()
        return queryset

    @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('amountingredient_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        amount_ing_create = [
            AmountIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        AmountIngredient.objects.bulk_create(amount_ing_create)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('amountingredient_set', None)
        tags = validated_data.pop('tags', None)
        if ingredients is not None:
            instance.ingredients.clear()

            ingredients_create = [
                AmountIngredient(
                    recipe=instance,
                    ingredient=ingredient['ingredient'],
                    amount=ingredient['amount']
                )
                for ingredient in ingredients
            ]
            AmountIngredient.objects.bulk_create(ingredients_create)

        if tags is not None:
            instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        self.fields['tags'] = TagSerializer(many=True)
        representation = super().to_representation(instance)
        return representation


class RecipeFollowSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов для подписок."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок на пользователей."""
    email = serializers.SlugRelatedField(source='following',
                                         slug_field='email',
                                         read_only=True)
    id = serializers.SlugRelatedField(source='following',
                                      slug_field='id',
                                      read_only=True)
    username = serializers.SlugRelatedField(source='following',
                                            slug_field='username',
                                            read_only=True)
    first_name = serializers.SlugRelatedField(source='following',
                                              slug_field='first_name',
                                              read_only=True)
    last_name = serializers.SlugRelatedField(source='following',
                                             slug_field='last_name',
                                             read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField(source='following.recipes')
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        if not self.context:
            return RecipeFollowSerializer(
                Recipe.objects.filter(author=obj.following), many=True
            ).data
        if 'recipes_limit' in self.context.get('request').query_params:
            limit = int(
                self.context.get('request').query_params.get('recipes_limit')
            )
            return RecipeFollowSerializer(
                Recipe.objects.filter(author=obj.following)[:limit], many=True
            ).data
        return RecipeFollowSerializer(
            Recipe.objects.filter(author=obj.following), many=True
        ).data

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(following=obj.following_id,
                                     user=obj.user_id).exists()

    def get_recipes_count(self, obj):
        author = obj.following_id
        return len(Recipe.objects.filter(author=author))


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в избранное."""
    id = serializers.SlugRelatedField(source='recipe',
                                      slug_field='id',
                                      read_only=True)
    name = serializers.SlugRelatedField(source='recipe',
                                        slug_field='name',
                                        read_only=True)
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.SlugRelatedField(source='recipe',
                                                slug_field='cooking_time',
                                                read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в корзину."""
    id = serializers.SlugRelatedField(source='recipe',
                                      slug_field='id',
                                      read_only=True)
    name = serializers.SlugRelatedField(source='recipe',
                                        slug_field='name',
                                        read_only=True)
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.SlugRelatedField(source='recipe',
                                                slug_field='cooking_time',
                                                read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')
