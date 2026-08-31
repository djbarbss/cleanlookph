from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Product


class ProductApiPermissionTests(TestCase):
    def test_catalogue_is_public_but_product_creation_requires_staff(self):
        payload = {"name": "Test product", "description": "Test", "price": "100.00", "stock": 2}

        self.assertEqual(self.client.get("/api/products/").status_code, 200)
        self.assertEqual(self.client.post("/api/products/", payload).status_code, 403)

        staff = get_user_model().objects.create_user(
            username="staff", email="staff@example.com", password="secure-password-123", is_staff=True
        )
        self.client.force_login(staff)
        self.assertEqual(self.client.post("/api/products/", payload).status_code, 201)
        self.assertTrue(Product.objects.filter(name="Test product").exists())
