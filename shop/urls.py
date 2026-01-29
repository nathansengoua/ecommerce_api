from django.urls import path
from .views import ProductCreateView, ProductListView

urlpatterns = [
    path("products/", ProductListView.as_view()),
    path("products/create/", ProductCreateView.as_view()),
]
