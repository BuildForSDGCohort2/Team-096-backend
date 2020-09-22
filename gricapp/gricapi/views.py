"""
Create views here
"""
from gricapi.models import User, Profile, Produce
from gricapi.serializers import (
    UserSerializer, ProfileSerializer, ProduceSerializer
)
from rest_framework import status, viewsets
from rest_framework.response import Response


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
