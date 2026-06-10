from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0
	readonly_fields = (
		"product",
		"product_name",
		"product_price",
		"quantity",
		"line_total",
	)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"full_name",
		"payment_method",
		"payment_status",
		"status",
		"total",
		"created_at",
	)
	list_filter = ("payment_method", "payment_status", "status", "created_at")
	search_fields = ("full_name", "email", "phone")
	inlines = [OrderItemInline]
