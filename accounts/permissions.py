from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class IsVendor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "vendor"


class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "client"


class IsAdminOrVendor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ["admin", "vendor"]
        )

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == "admin" or obj.owner == request.user
'''
from rest_framework.permissions import BasePermission, SAFE_METHODS


class ProductPermission(BasePermission):
    """
    GET, HEAD, OPTIONS  -> any authenticated user
    POST               -> admin, vendor
    PUT, PATCH         -> admin, vendor
    DELETE             -> admin only
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Read-only access
        if request.method in SAFE_METHODS:
            return True

        # Create / Update
        if request.method in ["POST", "PUT", "PATCH"]:
            return user.role in ["admin", "vendor"]

        # Delete
        if request.method == "DELETE":
            return user.role == "admin"

        return False


'''