from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class UserSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class MyUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.subscriber.filter(author=obj).exists()


class RecipeUser(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class SubscriptionSerializer(RecipeUser):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj)
        return RecipeUser(
            queryset,
            many=True
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.subscriber.filter(author=obj).exists()


class RecipesIngredientsSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient

        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )

    def validate_amount(self, amount):
        if amount <= 0:
            raise serializers.ValidationError(
                'Значение должно быть больше 0.'
            )
        return amount


class ToWriteTagsRecipies(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return TagSerializer(value).data


class RecipeSerializer(serializers.ModelSerializer):
    tags = ToWriteTagsRecipies(
        queryset=Tag.objects.all(),
        many=True,
    )
    author = MyUserSerializer(read_only=True)
    ingredients = IngredientWriteSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time'
                  )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.favorite.filter(
            user=user,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.shopping_cart.filter(
            user=user,
        ).exists()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.add_ingredients(ingredients_data, recipe)
        recipe.save()
        return recipe

    def validate(self, data):
        ingredients = data.pop('ingredients')
        ingredient_list = []
        for item in ingredients:
            ingredient = get_object_or_404(
                Ingredient,
                id=item['id']
            )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиент уже добавлен'
                )
            ingredient_list.append(ingredient)
        data['ingredients'] = ingredients
        return data

    def add_ingredients(self, ingredients, recipe):
        for item in ingredients:
            amount = item.get('amount')
            ingredient = get_object_or_404(
                Ingredient,
                pk=item['id'])
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        RecipeIngredient.objects.filter(
            recipe=instance
        ).delete()
        self.add_ingredients(ingredients_data, instance)
        instance.save()
        return instance


class RecipeSerializerGet(RecipeSerializer):
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    ingredients = RecipesIngredientsSerializer(
        many=True,
        source='recipeingredient_set',
    )

    class Meta:
        model = Recipe
        fields = '__all__'
