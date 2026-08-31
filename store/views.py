from django.shortcuts import render

# Create your views here.
def store_view(request):
    return render(request, "store/store.html")

def product_view(request, product_id):
    return render(request, "store/product.html", {
        "product_id": product_id
    })

# views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.filters import OrderingFilter

from .models import Product
from .serializers import ProductSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def get_permissions(self):
        # Browsing the catalogue is public; only staff can change it.
        if self.action in {"list", "retrieve", "latest"}:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        return Product.objects.all()

    @action(detail=False, methods=["get"])
    def latest(self, request):
        products = Product.objects.all().order_by("-created_at")[:6]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
