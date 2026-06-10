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
        print(product_id);
        quantity = int(request.data.get("quantity", 1))

        CartService.add_to_cart(
            request.user,
            product_id,
            quantity
        )

        return Response({"message": "Added to cart"})
    
    def update(self, request, pk=None):
        quantity = int(request.data.get("quantity", 1))

        cart = CartService.get_or_create_cart(request.user)

        try:
            cart_item = cart.items.get(id=pk)
            print(cart_item)
            # remove item if quantity <= 0
            if quantity <= 0:
                cart_item.delete()
                return Response({"message": "Item removed"})

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
        CartService.remove_item(request.user, pk)
        return Response({"message": "Item removed"})

    def delete_all(self, request):
        CartService.clear_cart(request.user)
        return Response({"message": "Cart cleared"})