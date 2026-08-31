from decimal import Decimal

from django.conf import settings
from django.db import models

from store.models import Product


class Order(models.Model):
	class PaymentMethod(models.TextChoices):
		COD = "cod", "Cash on Delivery"
		GCASH = "gcash", "GCash"
		CARD = "card", "Card"

	class PaymentStatus(models.TextChoices):
		PENDING = "pending", "Pending"
		PAID = "paid", "Paid"
		FAILED = "failed", "Failed"

	class Status(models.TextChoices):
		PLACED = "placed", "Placed"
		PROCESSING = "processing", "Processing"
		COMPLETED = "completed", "Completed"
		CANCELLED = "cancelled", "Cancelled"

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="orders"
	)
	full_name = models.CharField(max_length=255)
	email = models.EmailField()
	phone = models.CharField(max_length=32)
	address = models.CharField(max_length=255)
	city = models.CharField(max_length=100)
	province = models.CharField(max_length=100)
	zip_code = models.CharField(max_length=20)
	region = models.CharField(max_length=100, blank=True, default="")

	payment_method = models.CharField(
		max_length=20,
		choices=PaymentMethod.choices
	)
	payment_status = models.CharField(
		max_length=20,
		choices=PaymentStatus.choices,
		default=PaymentStatus.PENDING
	)
	status = models.CharField(
		max_length=20,
		choices=Status.choices,
		default=Status.PLACED
	)

	subtotal = models.DecimalField(max_digits=10, decimal_places=2)
	shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("120.00"))
	total = models.DecimalField(max_digits=10, decimal_places=2)

	gateway_provider = models.CharField(max_length=32, blank=True, default="")
	gateway_checkout_session_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
	gateway_checkout_url = models.URLField(blank=True, default="")
	payment_details = models.JSONField(default=dict, blank=True)
	# Stock is reserved when an order is created and released only once if it fails.
	inventory_released = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Order #{self.pk} - {self.full_name}"


class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
	product_name = models.CharField(max_length=255)
	product_price = models.DecimalField(max_digits=10, decimal_places=2)
	quantity = models.PositiveIntegerField()
	line_total = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return f"{self.product_name} x {self.quantity}"
