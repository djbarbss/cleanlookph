from django.urls import path 
from checkout import views 

urlpatterns = [
    path("checkout/", views.checkout_view, name="checkout"),
    path("orders/", views.orders_view, name="orders"),
    path("orders/<int:order_id>/", views.order_detail_view, name="order_detail"),
    path("api/checkout/", views.CheckoutAPIView.as_view(), name="checkout"),
    path("checkout/payment/success/", views.payment_return_view, {"outcome": "success"}, name="payment_success"),
    path("checkout/payment/cancel/", views.payment_return_view, {"outcome": "cancel"}, name="payment_cancel"),
] 