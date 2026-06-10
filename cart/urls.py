from django.urls import path 
from cart import views 

urlpatterns = [
    path("cart/", views.cart_view, name="cart")
] 
# cart/urls.py

cart_list = views.CartViewSet.as_view({
    "get": "list",
    "post": "create"
})

cart_item = views.CartViewSet.as_view({
    "delete": "destroy",
    "put": "update"
})

cart_clear = views.CartViewSet.as_view({
    "delete": "delete_all"
})

urlpatterns += [
    path("api/cart/", cart_list),
    path("api/cart/<int:pk>/", cart_item),
    path("api/cart/clear/", cart_clear),
]