from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Payment

# Category admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    search_fields = ['name']

# Product admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'stock_quantity', 'category']
    list_filter = ['category']
    search_fields = ['name']

# Inline OrderItem for admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

# Order admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    inlines = [OrderItemInline]

# Payment admin
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'method', 'status', 'paid_at']
    list_filter = ['status', 'method']
