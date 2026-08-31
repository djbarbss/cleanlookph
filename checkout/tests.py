from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from cart.models import Cart, CartItem
from store.models import Product

from .models import Order
from .gateway import PayMongoGateway


User = get_user_model()


class CheckoutAPIViewTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="checkout_user",
			email="checkout@example.com",
			password="password123"
		)
		self.client.force_authenticate(user=self.user)

		self.product = Product.objects.create(
			name="Reverse Hoodie",
			description="Inside-out construction",
			price=Decimal("1299.00"),
			stock=10,
		)

		cart = Cart.objects.create(user=self.user)
		CartItem.objects.create(cart=cart, product=self.product, quantity=1)

	def _payload(self, payment_method, **extra):
		payload = {
			"full_name": "Clean Girl",
			"email": "buyer@example.com",
			"phone": "+63 912 345 6789",
			"address": "123 Main St",
			"city": "Cebu City",
			"province": "Cebu",
			"zip": "6000",
			"region": "Central Visayas",
			"payment_method": payment_method,
		}
		payload.update(extra)
		return payload

	def test_cod_checkout_creates_order_and_clears_cart(self):
		response = self.client.post(
			reverse("checkout"),
			self._payload("cod"),
			format="json"
		)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(Order.objects.count(), 1)
		self.assertEqual(CartItem.objects.count(), 0)

		order = Order.objects.get()
		self.assertEqual(order.payment_method, Order.PaymentMethod.COD)
		self.assertEqual(order.payment_status, Order.PaymentStatus.PENDING)
		self.assertEqual(order.status, Order.Status.PLACED)
		self.assertEqual(order.subtotal, Decimal("1299.00"))
		self.assertEqual(order.total, Decimal("1419.00"))

	def test_gcash_checkout_returns_gateway_url(self):
		original_create = PayMongoGateway.create_checkout_session
		PayMongoGateway.create_checkout_session = lambda self, order, cart_items: {
			"checkout_session_id": "cs_test_123",
			"checkout_url": "https://checkout.paymongo.com/test-session"
		}
		try:
			response = self.client.post(
				reverse("checkout"),
				self._payload("gcash"),
				format="json"
			)
		finally:
			PayMongoGateway.create_checkout_session = original_create

		self.assertEqual(response.status_code, 201)
		payload = response.json()
		self.assertEqual(payload["checkout_url"], "https://checkout.paymongo.com/test-session")

		order = Order.objects.get()
		self.assertEqual(order.payment_method, Order.PaymentMethod.GCASH)
		self.assertEqual(order.payment_status, Order.PaymentStatus.PENDING)
		self.assertEqual(order.gateway_checkout_session_id, "cs_test_123")

	def test_card_checkout_returns_gateway_url(self):
		original_create = PayMongoGateway.create_checkout_session
		PayMongoGateway.create_checkout_session = lambda self, order, cart_items: {
			"checkout_session_id": "cs_test_456",
			"checkout_url": "https://checkout.paymongo.com/test-card-session"
		}
		try:
			response = self.client.post(
				reverse("checkout"),
				self._payload("card"),
				format="json"
			)
		finally:
			PayMongoGateway.create_checkout_session = original_create

		self.assertEqual(response.status_code, 201)
		payload = response.json()
		self.assertEqual(payload["checkout_url"], "https://checkout.paymongo.com/test-card-session")

		order = Order.objects.get()
		self.assertEqual(order.payment_method, Order.PaymentMethod.CARD)
		self.assertEqual(order.payment_status, Order.PaymentStatus.PENDING)
		self.assertEqual(order.gateway_checkout_session_id, "cs_test_456")

	def test_payment_return_success_marks_order_paid(self):
		original_create = PayMongoGateway.create_checkout_session
		original_retrieve = PayMongoGateway.retrieve_checkout_session
		PayMongoGateway.create_checkout_session = lambda self, order, cart_items: {
			"checkout_session_id": "cs_test_789",
			"checkout_url": "https://checkout.paymongo.com/test-return-session"
		}
		PayMongoGateway.retrieve_checkout_session = lambda self, session_id: {
			"id": session_id,
			"payment_status": "paid",
			"status": "paid",
			"metadata": {"order_id": "1"},
		}
		try:
			self.client.post(reverse("checkout"), self._payload("gcash"), format="json")
			self.client.force_login(self.user)
			response = self.client.get(reverse("payment_success") + "?order_id=1")
		finally:
			PayMongoGateway.create_checkout_session = original_create
			PayMongoGateway.retrieve_checkout_session = original_retrieve

		self.assertEqual(response.status_code, 200)
		order = Order.objects.get()
		self.assertEqual(order.payment_status, Order.PaymentStatus.PAID)
		self.assertEqual(order.status, Order.Status.PROCESSING)


class OrdersPageTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="orders_user",
			email="orders@example.com",
			password="password123"
		)
		self.client.force_login(self.user)

		self.order = Order.objects.create(
			user=self.user,
			full_name="Clean Girl",
			email="buyer@example.com",
			phone="09171234567",
			address="123 Main St",
			city="Cebu City",
			province="Cebu",
			zip_code="6000",
			region="Central Visayas",
			payment_method=Order.PaymentMethod.COD,
			payment_status=Order.PaymentStatus.PENDING,
			status=Order.Status.PLACED,
			subtotal=Decimal("1299.00"),
			shipping_fee=Decimal("120.00"),
			total=Decimal("1419.00"),
		)

	def test_orders_page_shows_list_and_detail(self):
		response = self.client.get(reverse("orders"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Your Orders")
		self.assertContains(response, "Order List")
		self.assertContains(response, "Clean Girl")

	def test_order_detail_page_shows_selected_order(self):
		response = self.client.get(reverse("order_detail", args=[self.order.id]))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, f"Order #{self.order.id}")
		self.assertContains(response, "Clean Girl")
