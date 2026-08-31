# cart/services.py

from django.core.exceptions import ValidationError

from .models import Cart, CartItem
from store.models import Product


class CartService:

    @staticmethod
    def get_or_create_cart(user):
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    def add_to_cart(user, product_id, quantity=1):

        if quantity < 1:
            raise ValidationError("Quantity must be at least one.")

        cart = CartService.get_or_create_cart(user)
        product = Product.objects.get(id=product_id)

        item = CartItem.objects.filter(cart=cart, product=product).first()
        new_quantity = item.quantity + quantity if item else quantity
        if new_quantity > product.stock:
            raise ValidationError("The requested quantity is not available.")
        if item is None:
            item = CartItem(cart=cart, product=product, quantity=new_quantity)
        else:
            item.quantity = new_quantity

        item.save()

        return item

    @staticmethod
    def remove_item(user, product_id):

        cart = CartService.get_or_create_cart(user)

        CartItem.objects.filter(
            cart=cart,
            product_id=product_id
        ).delete()

    @staticmethod
    def clear_cart(user):

        cart = CartService.get_or_create_cart(user)
        cart.items.all().delete()
