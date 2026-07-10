# shop/views.py
import stripe
from decimal import Decimal, InvalidOperation

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q

from .models import Product, Cart, CartItem, Order, OrderItem
from .serializers import ProductSerializer, CartSerializer, OrderSerializer
from accounts.permissions import IsAdminOrVendor, IsOwnerOrAdmin, IsClient
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

# ─── Product Views ────────────────────────────────────────────────

class ProductListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminOrVendor()]
        return [IsAuthenticated()]

    def get(self, request):
        products = Product.objects.select_related('category', 'owner').all()

        search = request.query_params.get('search', '').strip()
        category = request.query_params.get('category', None)
        in_stock = request.query_params.get('in_stock', None)
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)

        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        if category:
            products = products.filter(category_id=category)

        if in_stock is not None:
            if in_stock.lower() in ['true', '1', 'yes', 'y']:
                products = products.filter(is_in_stock=True)
            elif in_stock.lower() in ['false', '0', 'no', 'n']:
                products = products.filter(is_in_stock=False)

        if min_price is not None:
            try:
                products = products.filter(price__gte=Decimal(min_price))
            except InvalidOperation:
                raise ValidationError({"min_price": "Must be a valid number."})

        if max_price is not None:
            try:
                products = products.filter(price__lte=Decimal(max_price))
            except InvalidOperation:
                raise ValidationError({"max_price": "Must be a valid number."})

        serializer = ProductSerializer(products.distinct(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)  # inject owner from token
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminOrVendor(), IsOwnerOrAdmin()]

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

        raw_quantity = request.data.get("quantity", item.quantity)
        try:
            quantity = int(raw_quantity)
        except (TypeError, ValueError):
            if created:
                item.delete()  # don't leave a stray zero-quantity row behind
            raise ValidationError({"quantity": "Must be an integer."})

        if quantity <= 0:
            if created:
                item.delete()
            raise ValidationError({"quantity": "Must be greater than zero."})

        if quantity > product.stock_quantity:
            if created:
                item.delete()
            raise ValidationError(
                {"quantity": f"Only {product.stock_quantity} unit(s) of '{product.name}' in stock."}
            )

        item.quantity = quantity
        item.save()

        message = "Item added to cart." if created else "Cart updated."
        return Response({"message": message}, status=status.HTTP_200_OK)


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
        cart, _ = Cart.objects.get_or_create(owner=request.user)
        cart_items = cart.items.select_related("product")

        if not cart_items.exists():
            raise ValidationError({"detail": "Your cart is empty."})

        total = 0
        order = Order.objects.create(user=request.user, total_amount=0)

        # Lock product rows for the duration of the transaction to prevent
        # two concurrent checkouts from overselling the same stock.
        product_ids = [item.product_id for item in cart_items]
        locked_products = Product.objects.select_for_update().in_bulk(product_ids)

        for item in cart_items:
            product = locked_products[item.product_id]

            if product.stock_quantity < item.quantity:
                raise ValidationError(
                    {"detail": f"'{product.name}' does not have enough stock."}
                )

            product.stock_quantity -= item.quantity
            product.save()  # triggers model.save() → updates is_in_stock

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price
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