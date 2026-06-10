from django.db import models
from django.contrib import admin
# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(
        upload_to="products/",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name