from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.services import CartService
from store.models import Product

from .models import Order, OrderItem
from .gateway import PayMongoGateway, PaymentGatewayError
from .serializers import CheckoutSerializer


def release_inventory(order):
    """Return a failed/cancelled order's reserved stock once."""
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        if order.inventory_released:
            return order
        for item in order.items.select_related("product"):
            if item.product_id:
                Product.objects.filter(pk=item.product_id).update(stock=F("stock") + item.quantity)
        order.inventory_released = True
        order.save(update_fields=["inventory_released", "updated_at"])
    return order

@login_required
def checkout_view(request):
    return render(request, "checkout/checkout.html")


@login_required
def orders_view(request):
    orders = (
        request.user.orders
        .prefetch_related("items__product")
        .order_by("-created_at")
    )

    return render(request, "checkout/orders.html", {
        "orders": orders,
    })


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(
        request.user.orders.prefetch_related("items__product"),
        pk=order_id
    )

    return render(request, "checkout/order_detail.html", {
        "order": order,
    })


class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        cart = CartService.get_or_create_cart(request.user)
        cart_items = list(cart.items.select_related("product"))

        if not cart_items:
            return Response(
                {"error": "Your cart is empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        subtotal = sum(
            (item.product.price * item.quantity for item in cart_items),
            Decimal("0.00")
        )
        shipping_fee = Decimal("120.00")
        total = subtotal + shipping_fee

        payment_method = data["payment_method"]
        gateway = PayMongoGateway()

        with transaction.atomic():
            product_ids = [item.product_id for item in cart_items]
            products = {
                product.id: product
                for product in Product.objects.select_for_update().filter(id__in=product_ids)
            }
            for item in cart_items:
                product = products.get(item.product_id)
                if not product or product.stock < item.quantity:
                    return Response(
                        {"error": f"{item.product.name} no longer has enough stock."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            order = Order.objects.create(
                user=request.user,
                full_name=data["full_name"],
                email=data["email"],
                phone=data["phone"],
                address=data["address"],
                city=data["city"],
                province=data["province"],
                zip_code=data["zip"],
                region=data.get("region", ""),
                payment_method=payment_method,
                payment_status=Order.PaymentStatus.PENDING,
                status=Order.Status.PLACED,
                subtotal=subtotal,
                shipping_fee=shipping_fee,
                total=total,
                payment_details={"provider": "cash" if payment_method == Order.PaymentMethod.COD else "paymongo"},
            )

            for item in cart_items:
                line_total = item.product.price * item.quantity
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_price=item.product.price,
                    quantity=item.quantity,
                    line_total=line_total,
                )
                Product.objects.filter(pk=item.product_id).update(stock=F("stock") - item.quantity)

            if payment_method == Order.PaymentMethod.COD:
                cart.items.all().delete()
                return Response(
                    {
                        "message": "Order placed successfully.",
                        "order_id": order.id,
                        "payment_method": order.payment_method,
                        "payment_status": order.payment_status,
                        "order_status": order.status,
                        "total": str(order.total),
                    },
                    status=status.HTTP_201_CREATED
                )

        try:
            session = gateway.create_checkout_session(order, cart_items)
        except PaymentGatewayError as error:
            order.payment_status = Order.PaymentStatus.FAILED
            order.status = Order.Status.CANCELLED
            order.payment_details = {
                "provider": "paymongo",
                "error": str(error),
            }
            order.save(update_fields=["payment_status", "status", "payment_details", "updated_at"])
            release_inventory(order)

            return Response(
                {"error": str(error)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        order.gateway_provider = "paymongo"
        order.gateway_checkout_session_id = session["checkout_session_id"]
        order.gateway_checkout_url = session["checkout_url"]
        order.payment_details = {
            "provider": "paymongo",
            "payment_method": payment_method,
        }
        order.save(update_fields=[
            "gateway_provider",
            "gateway_checkout_session_id",
            "gateway_checkout_url",
            "payment_details",
            "updated_at",
        ])

        return Response(
            {
                "message": "Redirecting to payment gateway.",
                "order_id": order.id,
                "payment_method": order.payment_method,
                "payment_status": order.payment_status,
                "order_status": order.status,
                "checkout_url": order.gateway_checkout_url,
                "total": str(order.total),
            },
            status=status.HTTP_201_CREATED
        )


@login_required
def payment_return_view(request, outcome):
    order_id = request.GET.get("order_id")
    order = get_object_or_404(request.user.orders, pk=order_id) if order_id else None

    if not order:
        raise Http404("Order not found")

    gateway = PayMongoGateway()

    if outcome == "success" and order.gateway_checkout_session_id:
        try:
            session = gateway.retrieve_checkout_session(order.gateway_checkout_session_id)
        except PaymentGatewayError:
            session = None

        if session and session["metadata"].get("order_id") == str(order.id) and session["payment_status"] == "paid":
            order.payment_status = Order.PaymentStatus.PAID
            order.status = Order.Status.PROCESSING
            order.save(update_fields=["payment_status", "status", "updated_at"])
            CartService.clear_cart(order.user)

    elif outcome == "cancel" and order.payment_status != Order.PaymentStatus.PAID:
        order.payment_status = Order.PaymentStatus.FAILED
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["payment_status", "status", "updated_at"])
        release_inventory(order)

    return render(request, "checkout/payment_result.html", {
        "order": order,
        "outcome": outcome,
    })
