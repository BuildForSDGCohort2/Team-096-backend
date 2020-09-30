"""
Create views here
"""
from gricapi.models import User, Produce
from gricapi.serializers import (
    UserSerializer, ProduceSerializer
)
from rest_framework import viewsets


class UserViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Return the given user.

    list:
    Return a list of all the existing users.

    create:
    Create a new user instance.

    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProduceViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Return the given produce.

    list:
    Return a list of all the existing produce.

    create:
    Create a new produce instance.

    """
    queryset = Produce.objects.all()
    serializer_class = ProduceSerializer
