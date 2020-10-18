"""
Create views here
"""
from gricapi.models import User, Produce, Category, Order
from gricapi.serializers import (
    UserSerializer, ProduceSerializer, CategoryProduceSerializer,
    OrderCreateSerializer, OrderListSerializer
)
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (
    AllowAny, IsAuthenticated
)

from gricapi.mixins import (
    CreateModelMixin, UpdateModelMixin,
    ListModelMixin, RetrieveModelMixin
)
from gricapi.generics import GenericAPIView
from gricapi.permissions import (
    IsAdminUser, IsAdminOrAnonymousUser, IsOwnerOrAdmin
)


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

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action == 'list':
            permission_classes = [IsAuthenticated]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            permission_classes = [IsAdminOrAnonymousUser]
        elif self.action == 'destroy':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    # pylint: disable=unused-argument,no-self-use
    def destroy(self, request, *args, **kwargs):
        response = {'message': 'Delete function is not offered in this path.'}
        return Response(response, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ProduceViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Return the given produce.

    list:
    Return a list of all the existing produce.

    create:
    Create a new produce instance.

    Update:
    The update produce attributes except date_created and date_modified.
    Date_modified is updated automatically upon successful serializer
    validation.

    Destroy:
    Delete the produce instance.
    Produce can only be deleted by the owner or staff

    """
    queryset = Produce.objects.all()
    serializer_class = ProduceSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsOwnerOrAdmin]
        elif self.action == 'destroy':
            permission_classes = [IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def destroy(self, request, pk=None):  # pylint: disable=unused-argument
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProduceCategoryViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Return the given category and corresponding produces.

    list:
    Return a list of all the existing categories.

    create:
    Create a new category and produce instance.

    Update:
    The update method is not allowed for this viewSets

    Destroy:
    Delete the category from list of Categories and change all
    corresponding products to 'General' category.

    """
    queryset = Category.objects.all()
    serializer_class = CategoryProduceSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action in ['create', 'list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsOwnerOrAdmin]
        elif self.action == 'destroy':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    # pylint: disable=unused-argument,no-self-use
    def update(self, request, *args, **kwargs):
        response = {'message': 'Update function is not offered in this path.'}
        return Response(response, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # pylint: disable=unused-argument
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not (request.user.is_superuser):
            return Response(status=status.HTTP_403_FORBIDDEN)
        new_category, created = Category.objects.get_or_create(
            category_name="General")
        if created:
            pass
        products = Produce.objects.filter(produce_category=instance)
        for product in products:
            product.produce_category = new_category
            product.save()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(CreateModelMixin,
                   UpdateModelMixin,
                   ListModelMixin,
                   RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   GenericAPIView,
                   viewsets.GenericViewSet):
    """
    retrieve:
    Return an Order and corresponding items.

    list:
    Return a list of all orders by the user.

    create:
    Create a new order.

    Update:
    Add and item to an order.

    Destroy:
    Delete an order and corresponding items.

    """
    queryset = Order.objects.all()
    read_serializer_class = OrderListSerializer
    serializer_class = read_serializer_class
    write_serializer_class = OrderCreateSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action in ['create', 'list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsOwnerOrAdmin]
        elif self.action == 'destroy':
            permission_classes = [IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        Determines which serializer to order `list` or `detail`
        """
        if self.action in ['create', 'update', 'destroy']:
            if hasattr(self, 'write_serializer_class'):
                return self.write_serializer_class
        return self.read_serializer_class

    # pylint: disable=unused-argument
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        items = instance.items.all()
        for item in items:
            item.delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
