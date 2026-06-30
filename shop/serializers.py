# shop/serializers.py
from rest_framework import serializers
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Payment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class ProductSerializer(serializers.ModelSerializer):
    # By default category would return just the FK integer.
    # This shows the category name instead — read only, just for display.
    category_name = serializers.CharField(source='category.name', read_only=True)
    owner_email = serializers.CharField(source='owner.email', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price',
            'stock_quantity', 'is_in_stock',
            'category',       # accepts category ID on write
            'category_name',  # shows category name on read
            'owner_email',
            'created_at'
        ]
        # is_in_stock is auto-computed in model.save() — no point accepting it as input
        read_only_fields = ['is_in_stock', 'created_at', 'owner_email', 'category_name']


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price', max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity']
        read_only_fields = ['product_name', 'product_price']


class CartSerializer(serializers.ModelSerializer):
    # 'items' is the related_name on CartItem → Cart
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'owner', 'items', 'created_at']
        read_only_fields = ['owner', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']
        read_only_fields = ['product_name']


class OrderSerializer(serializers.ModelSerializer):
    # 'items' is the related_name on OrderItem → Order
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_amount', 'items', 'created_at', 'updated_at']
        read_only_fields = ['user', 'total_amount', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'method', 'status', 'paid_at']
        read_only_fields = ['paid_at']