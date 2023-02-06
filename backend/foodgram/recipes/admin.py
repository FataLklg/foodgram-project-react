from django.contrib import admin

from .models import (AmountIngredient, Favorite, Follow, Ingredient, Recipe,
                     ShoppingCart, Tag)


class CountInline(admin.TabularInline):
    model = AmountIngredient
    extra = 1
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    inlines = (CountInline,)
    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )
    list_filter = ('name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (CountInline,)
    list_display = (
        'pk',
        'author',
        'name',
        'text',
        'image',
        'get_ingredients',
        'get_tags',
        'cooking_time',
        'get_count_add_to_favorite'
    )
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    def get_ingredients(self, obj):
        return '\n'.join([i.name + ',' for i in obj.ingredients.all()])
    get_ingredients.short_description = 'Ингредиенты'

    def get_tags(self, obj):
        return '\n'.join([t.name + ',' for t in obj.tags.all()])
    get_tags.short_description = 'Теги'

    def get_count_add_to_favorite(self, obj):
        return len(Favorite.objects.filter(recipe=obj))
    get_count_add_to_favorite.short_description = 'Кол-во в избранном'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'following'
    )
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe'
    )
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShopingCartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe'
    )
    empty_value_display = '-пусто-'
