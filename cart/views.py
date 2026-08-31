from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def cart_view(request):
    return render(request, "cart/cart.html")

# Viewsets
# cart/views.py

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from store.models import Product

from .models import Cart
from .serializers import CartSerializer
from .services import CartService


class CartViewSet(ViewSet):

    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart = CartService.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def create(self, request):
        product_id = request.data.get("product_id")
        try:
            quantity = int(request.data.get("quantity", 1))
        except (TypeError, ValueError):
            return Response({"error": "Quantity must be a whole number."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            CartService.add_to_cart(request.user, product_id, quantity)
        except (ValidationError, ValueError) as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Added to cart"})
    
    def update(self, request, pk=None):
        try:
            quantity = int(request.data.get("quantity", 1))
        except (TypeError, ValueError):
            return Response({"error": "Quantity must be a whole number."}, status=status.HTTP_400_BAD_REQUEST)

        cart = CartService.get_or_create_cart(request.user)

        try:
            cart_item = cart.items.get(id=pk)
            # remove item if quantity <= 0
            if quantity <= 0:
                cart_item.delete()
                return Response({"message": "Item removed"})

            if quantity > cart_item.product.stock:
                return Response({"error": "The requested quantity is not available."}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = quantity
            cart_item.save()

            return Response({
                "message": "Quantity updated",
                "quantity": cart_item.quantity
            })

        except cart.items.model.DoesNotExist:
            return Response(
                {"error": "Cart item not found"},
                status=404
            )

    def destroy(self, request, pk=None):
        cart = CartService.get_or_create_cart(request.user)
        cart_item = get_object_or_404(cart.items, pk=pk)
        cart_item.delete()
        return Response({"message": "Item removed"})

    def delete_all(self, request):
        CartService.clear_cart(request.user)
        return Response({"message": "Cart cleared"})
