# shop/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError   # ← was missing before
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Product, Cart, CartItem, Order, OrderItem
from .serializers import ProductSerializer, CartSerializer, OrderSerializer  # ← now imported
from accounts.permissions import IsAdminOrVendor, IsOwnerOrAdmin, IsClient


# ─── Product Views ────────────────────────────────────────────────

class ProductListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.select_related('category', 'owner').all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Permission check — only vendor or admin can create products
        if request.user.role not in ["vendor", "admin"]:
            return Response(
                {"detail": "Only vendors or admins can create products."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)  # inject owner from token
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrVendor, IsOwnerOrAdmin]

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        self.check_object_permissions(request, product)

        # partial=True means you don't have to send all fields
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        self.check_object_permissions(request, product)
        product.delete()
        return Response({"message": "Product deleted."}, status=status.HTTP_204_NO_CONTENT)


# ─── Cart Views ───────────────────────────────────────────────────

class CartDetailView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(owner=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemAddUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(owner=request.user)
        product = get_object_or_404(Product, id=request.data.get("product_id"))

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        item.quantity = request.data.get("quantity", item.quantity)
        item.save()

        return Response({"message": "Cart updated."}, status=status.HTTP_200_OK)


class CartItemRemoveView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def delete(self, request, product_id):
        cart = get_object_or_404(Cart, owner=request.user)
        item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        item.delete()
        return Response({"message": "Item removed."}, status=status.HTTP_204_NO_CONTENT)


class CartClearView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def post(self, request):
        cart = get_object_or_404(Cart, owner=request.user)
        cart.items.all().delete()
        return Response({"message": "Cart cleared."}, status=status.HTTP_200_OK)


# ─── Checkout & Orders ────────────────────────────────────────────

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        # ← was Cart.objects.get(user=...) — model field is 'owner'
        cart, _ = Cart.objects.get_or_create(owner=request.user)
        cart_items = cart.items.select_related("product")

        if not cart_items.exists():
            raise ValidationError({"detail": "Your cart is empty."})

        total = 0
        order = Order.objects.create(user=request.user, total_amount=0)

        for item in cart_items:
            product = item.product

            if product.stock_quantity < item.quantity:
                # Raises a 400 — rolls back the transaction automatically
                raise ValidationError(
                    {"detail": f"'{product.name}' does not have enough stock."}
                )

            product.stock_quantity -= item.quantity
            product.save()  # triggers model.save() → updates is_in_stock

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price   # ← was price_at_purchase, model field is 'price'
            )

            total += product.price * item.quantity

        order.total_amount = total
        order.save()

        cart.items.all().delete()

        return Response(
            {"message": "Order placed.", "order_id": order.id},
            status=status.HTTP_201_CREATED
        )


class MyOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)