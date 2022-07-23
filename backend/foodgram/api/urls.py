from django.urls import include, path
from rest_framework import routers

from api.views import (IngredientViewSet, MyUserViewSet, RecipeViewSet,
                       TagViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipe')
router_v1.register('tags', TagViewSet, basename='tag')
router_v1.register('ingredients', IngredientViewSet, basename='ingredient')
router_v1.register('users', MyUserViewSet, basename='user')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
