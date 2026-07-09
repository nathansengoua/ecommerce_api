from django.urls import path
from .views import (
    ProductListCreateView,
    ProductDetailView,
    CartDetailView,
    CartItemAddUpdateView,
    CartItemRemoveView,
    CartClearView,
    CheckoutView,
    MyOrdersView,
)

urlpatterns = [
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path("products/create/", ProductListCreateView.as_view(), name="product-create"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("cart/", CartDetailView.as_view(), name="cart-detail"),
    path("cart/add/", CartItemAddUpdateView.as_view(), name="cart-add"),
    path("cart/remove/<int:product_id>/", CartItemRemoveView.as_view(), name="cart-remove"),
    path("cart/clear/", CartClearView.as_view(), name="cart-clear"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("orders/", MyOrdersView.as_view(), name="orders"),
]
