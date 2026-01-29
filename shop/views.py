from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Product
from accounts.permissions import IsAdminOrVendor


class ProductListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.all()
        data = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "stock_quantity": p.stock_quantity,
                "is_in_stock": p.is_in_stock,
                "category": p.category.name,
                "owner": p.owner.email,
            }
            for p in products
        ]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.role not in ["vendor", "admin"]:
            return Response(
                {"detail": "Only vendors or admins can create products."},
                status=status.HTTP_403_FORBIDDEN
            )

        product = Product.objects.create(
            owner=request.user,
            name=request.data.get("name"),
            description=request.data.get("description"),
            price=request.data.get("price"),
            stock_quantity=request.data.get("stock_quantity", 0),
            category_id=request.data.get("category"),
        )

        return Response(
            {"message": "Product created successfully", "product_id": product.id},
            status=status.HTTP_201_CREATED
        )

from django.shortcuts import get_object_or_404
from accounts.permissions import IsAdminOrVendor, IsOwnerOrAdmin


class ProductDetailView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsAdminOrVendor,
        IsOwnerOrAdmin,
    ]

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        self.check_object_permissions(request, product)

        product.name = request.data.get("name", product.name)
        product.description = request.data.get("description", product.description)
        product.price = request.data.get("price", product.price)
        product.stock_quantity = request.data.get(
            "stock_quantity", product.stock_quantity
        )
        product.category_id = request.data.get(
            "category", product.category_id
        )

        product.save()

        return Response(
            {"message": "Product updated successfully"},
            status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        self.check_object_permissions(request, product)

        product.delete()
        return Response(
            {"message": "Product deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )