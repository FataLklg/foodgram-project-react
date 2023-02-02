from rest_framework import mixins, viewsets


class TokenCreateCustomViewSet(mixins.CreateModelMixin,
                               viewsets.GenericViewSet):
    pass
