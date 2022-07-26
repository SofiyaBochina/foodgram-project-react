from django.contrib import admin

from foodgram.settings import EMPTY_CONST

from .models import Favorite, Ingredient, Recipe, Subscription, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = []
    list_display = (
        'pk',
        'author',
        'get_tags',
        'get_ingredients',
        'name',
        'text',
        'cooking_time',
        'image'
    )
    search_fields = ('name', 'author')
    list_filter = ('name', 'author')
    empty_value_display = EMPTY_CONST


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    empty_value_display = EMPTY_CONST


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = EMPTY_CONST


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')
    empty_value_display = EMPTY_CONST


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipes')
    search_fields = ('user', 'recipes')
    list_filter = ('user', 'recipes')
    empty_value_display = EMPTY_CONST
