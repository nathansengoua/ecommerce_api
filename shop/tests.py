from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Category, Product


class ProductSearchFilterTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass",
            first_name="Admin",
            last_name="User",
            role="admin",
        )
        cls.vendor_user = User.objects.create_user(
            email="vendor@example.com",
            password="vendorpass",
            first_name="Vendor",
            last_name="User",
            role="vendor",
        )
        cls.vendor_user_2 = User.objects.create_user(
            email="vendor2@example.com",
            password="vendorpass2",
            first_name="Vendor2",
            last_name="User",
            role="vendor",
        )
        cls.client_user = User.objects.create_user(
            email="client@example.com",
            password="clientpass",
            first_name="Client",
            last_name="User",
            role="client",
        )

        cls.category_electronics = Category.objects.create(
            name="Electronics",
            description="Phones, laptops, accessories",
        )
        cls.category_books = Category.objects.create(
            name="Books",
            description="Programming and educational books",
        )
        cls.category_clothing = Category.objects.create(
            name="Clothing",
            description="Casual and formal wear",
        )
        cls.category_home = Category.objects.create(
            name="Home",
            description="Kitchen and home essentials",
        )

        cls.product_one = Product.objects.create(
            owner=cls.vendor_user,
            name="Wireless Mouse",
            description="Bluetooth mouse for laptops",
            price=Decimal("19.99"),
            stock_quantity=10,
            category=cls.category_electronics,
        )
        cls.product_two = Product.objects.create(
            owner=cls.vendor_user,
            name="Mechanical Keyboard",
            description="RGB gaming keyboard",
            price=Decimal("49.99"),
            stock_quantity=0,
            category=cls.category_electronics,
        )
        cls.product_three = Product.objects.create(
            owner=cls.vendor_user_2,
            name="USB-C Charger",
            description="Fast charging adapter",
            price=Decimal("14.50"),
            stock_quantity=8,
            category=cls.category_electronics,
        )
        cls.product_four = Product.objects.create(
            owner=cls.vendor_user_2,
            name="Python Book",
            description="Learn Django and DRF",
            price=Decimal("29.99"),
            stock_quantity=5,
            category=cls.category_books,
        )
        cls.product_five = Product.objects.create(
            owner=cls.vendor_user_2,
            name="Django Book",
            description="Build web apps with Django",
            price=Decimal("34.99"),
            stock_quantity=3,
            category=cls.category_books,
        )
        cls.product_six = Product.objects.create(
            owner=cls.vendor_user,
            name="White T-Shirt",
            description="Cotton casual t-shirt",
            price=Decimal("12.99"),
            stock_quantity=15,
            category=cls.category_clothing,
        )
        cls.product_seven = Product.objects.create(
            owner=cls.vendor_user,
            name="Denim Jacket",
            description="Classic denim jacket",
            price=Decimal("39.99"),
            stock_quantity=4,
            category=cls.category_clothing,
        )
        cls.product_eight = Product.objects.create(
            owner=cls.vendor_user_2,
            name="Ceramic Mug",
            description="Coffee mug for home use",
            price=Decimal("8.99"),
            stock_quantity=20,
            category=cls.category_home,
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.client_user)

    def test_seeded_users_categories_and_products_exist(self):
        self.assertTrue(get_user_model().objects.filter(email="admin@example.com").exists())
        self.assertTrue(get_user_model().objects.filter(email="vendor@example.com").exists())
        self.assertTrue(get_user_model().objects.filter(email="client@example.com").exists())
        self.assertEqual(Category.objects.count(), 4)
        self.assertGreaterEqual(Product.objects.count(), 8)

    def test_search_and_filter_return_expected_products(self):
        response = self.client.get(
            reverse("product-list-create"),
            {
                "search": "mouse",
                "category": self.category_electronics.id,
                "in_stock": "true",
                "min_price": "10",
                "max_price": "30",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.product_one.name)
