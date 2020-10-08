from django.contrib.auth.models import Group
from gricapi.models import Order, Produce
from rest_framework import permissions


def _is_in_group(user, group_name):
    """
    Takes a user and a group name, and returns `True`
    if the user is in that group.
    """
    try:
        return Group.objects.get(name=group_name).user_set.filter(
            id=user.id).exists()
    except Group.DoesNotExist:
        return None


def _has_group_permission(user, required_groups):
    return (
        any([_is_in_group(user, group_name) for group_name in required_groups])
    )


class IsAdminUser(permissions.BasePermission):
    # group_name for super admin
    required_groups = ['admin']

    def has_permission(self, request, view):
        has_group_permission = _has_group_permission(
            request.user, self.required_groups)
        return request.user and has_group_permission

    def has_object_permission(self, request, view, obj):
        has_group_permission = _has_group_permission(
            request.user, self.required_groups)
        return request.user and has_group_permission


class IsAdminOrAnonymousUser(permissions.BasePermission):
    required_groups = ['admin', 'anonymous']

    def has_permission(self, request, view):
        has_group_permission = _has_group_permission(
            request.user, self.required_groups)
        return request.user and has_group_permission


class IsOwnerOrAdmin(permissions.BasePermission):
    """Custom permission class to allow only product owners to edit them."""
    required_groups = ['admin']

    def has_object_permission(self, request, view, obj):
        """Return True if permission is granted to the owner."""
        has_group_permission = _has_group_permission(
            request.user, self.required_groups)

        if isinstance(obj, Order):
            return obj.consumer == request.user or has_group_permission
        if isinstance(obj, Produce):
            return obj.owner == request.user or has_group_permission

        return obj == request.user
