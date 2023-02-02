from rest_framework.pagination import PageNumberPagination


class CustomPaginations(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'limit'


class RecipesInFollowPaginations(PageNumberPagination):
    page_size = None
    page_size_query_param = 'recipes_limit'
