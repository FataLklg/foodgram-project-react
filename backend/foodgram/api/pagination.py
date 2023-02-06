from rest_framework.pagination import PageNumberPagination


class CustomPaginations(PageNumberPagination):
    """Пагинация для пользователей и рецептов."""
    page_size = 6
    page_size_query_param = 'limit'


class RecipesInFollowPaginations(PageNumberPagination):
    """Пагинация для рецептов в подписках."""
    page_size = 6
    page_size_query_param = 'recipes_limit'
