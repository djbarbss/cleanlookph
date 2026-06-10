# cart/services.py

from .models import Cart, CartItem
from store.models import Product


class CartService:

    @staticmethod
    def get_or_create_cart(user):
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    def add_to_cart(user, product_id, quantity=1):

        cart = CartService.get_or_create_cart(user)

        product = Product.objects.get(id=product_id)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity

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