from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FollowViewSet, IngredientVievSet, RecipeViewSet,
                    TagViewSet, TokenCreateViewSet, UserViewSet)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='Tags')
router.register('ingredients', IngredientVievSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('auth/token/login/', TokenCreateViewSet.as_view()),
    path('users/subscriptions/', FollowViewSet.as_view({'get': 'list'})),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
