from django.urls import path, include
from store import views 
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)

urlpatterns = [
    path("store/", views.store_view, name="store"),
    path("product/<int:product_id>/", views.product_view, name="product"),
    path('api/', include(router.urls)),
]