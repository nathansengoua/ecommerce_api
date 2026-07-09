from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from shop.models import Category, Product


class Command(BaseCommand):
    help = "Seed the database with admin, vendors, clients, categories, and products for local testing"

    def handle(self, *args, **options):
        User = get_user_model()

        admin_user, created = User.objects.get_or_create(
            email="admin@example.com",
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        if created:
            admin_user.set_password("adminpass")
            admin_user.save()

        vendor_users = []
        for email, first_name, last_name, password in [
            ("vendor1@example.com", "Vendor", "One", "vendorpass1"),
            ("vendor2@example.com", "Vendor", "Two", "vendorpass2"),
        ]:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": "vendor",
                    "is_staff": False,
                    "is_superuser": False,
                    "is_active": True,
                },
            )
            if created:
                user.set_password(password)
                user.save()
            vendor_users.append(user)

        client_users = []
        for email, first_name, last_name, password in [
            ("client1@example.com", "Client", "One", "clientpass1"),
            ("client2@example.com", "Client", "Two", "clientpass2"),
            ("client3@example.com", "Client", "Three", "clientpass3"),
            ("client4@example.com", "Client", "Four", "clientpass4"),
        ]:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": "client",
                    "is_staff": False,
                    "is_superuser": False,
                    "is_active": True,
                },
            )
            if created:
                user.set_password(password)
                user.save()
            client_users.append(user)

        category_names = ["Electronics", "Clothing", "Books", "Home"]
        category_descriptions = {
            "Electronics": "Phones, laptops, accessories",
            "Clothing": "Casual and formal wear",
            "Books": "Programming and educational books",
            "Home": "Kitchen and home essentials",
        }

        categories = {}
        for name in category_names:
            category, _ = Category.objects.get_or_create(
                name=name,
                defaults={"description": category_descriptions[name]},
            )
            categories[name] = category

        products = [
            ("Electronics", "Wireless Mouse", "Bluetooth mouse for laptops", Decimal("19.99"), 10),
            ("Electronics", "Mechanical Keyboard", "RGB gaming keyboard", Decimal("49.99"), 0),
            ("Electronics", "USB-C Charger", "Fast charging adapter", Decimal("14.50"), 8),
            ("Electronics", "Noise-Cancelling Headphones", "Over-ear wireless headphones", Decimal("89.99"), 5),
            ("Clothing", "White T-Shirt", "Cotton casual t-shirt", Decimal("12.99"), 15),
            ("Clothing", "Denim Jacket", "Classic denim jacket", Decimal("39.99"), 4),
            ("Clothing", "Black Sneakers", "Comfortable everyday sneakers", Decimal("34.99"), 12),
            ("Clothing", "Formal Shirt", "Smart business shirt", Decimal("24.99"), 7),
            ("Books", "Python Book", "Learn Django and DRF", Decimal("29.99"), 5),
            ("Books", "Django Book", "Build web apps with Django", Decimal("34.99"), 3),
            ("Books", "JavaScript Guide", "Frontend essentials", Decimal("21.99"), 9),
            ("Books", "System Design Basics", "Learn architecture and scaling", Decimal("27.99"), 6),
            ("Home", "Ceramic Mug", "Coffee mug for home use", Decimal("8.99"), 20),
            ("Home", "Throw Blanket", "Soft fleece blanket", Decimal("18.99"), 11),
            ("Home", "Desk Lamp", "LED desk lamp", Decimal("22.99"), 10),
            ("Home", "Scented Candle", "Relaxation candle", Decimal("9.99"), 14),
        ]

        owners = [vendor_users[0], vendor_users[1], admin_user]
        owner_index = 0

        for category_name, name, description, price, stock_quantity in products:
            owner = owners[owner_index % len(owners)]
            Product.objects.get_or_create(
                name=name,
                category=categories[category_name],
                defaults={
                    "owner": owner,
                    "description": description,
                    "price": price,
                    "stock_quantity": stock_quantity,
                },
            )
            owner_index += 1

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
        self.stdout.write("Admin login: admin@example.com / adminpass")
        self.stdout.write("Vendors: vendor1@example.com / vendorpass1, vendor2@example.com / vendorpass2")
        self.stdout.write("Clients: client1@example.com / clientpass1, client2@example.com / clientpass2, client3@example.com / clientpass3, client4@example.com / clientpass4")
        self.stdout.write("Categories and products seeded for local testing.")