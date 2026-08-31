from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import CartItem
from .services import CartService
from store.models import Product


class CartApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cart-user", email="cart@example.com", password="secure-password-123"
        )
        self.client.force_login(self.user)
        self.product = Product.objects.create(
            name="Cart product", description="Test", price=Decimal("100.00"), stock=2
        )

    def test_delete_uses_cart_item_id(self):
        item = CartService.add_to_cart(self.user, self.product.id)

        response = self.client.delete(f"/api/cart/{item.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(CartItem.objects.filter(pk=item.id).exists())

    def test_cart_rejects_quantity_above_stock(self):
        response = self.client.post(
            "/api/cart/", {"product_id": self.product.id, "quantity": 3}, content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(CartItem.objects.exists())
