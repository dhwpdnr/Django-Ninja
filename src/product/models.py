from django.db import models
from enum import Enum


class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"


class Product(models.Model):
    name = models.CharField(max_length=128)
    price = models.PositiveIntegerField()
    status = models.CharField(max_length=8)  # active | inactive | paused
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, related_name="products"
    )

    class Meta:
        app_label = "product"
        db_table = "product"
        indexes = [
            models.Index(fields=["status", "price"]),
        ]


class Category(models.Model):
    name = models.CharField(max_length=32)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="children"
    )

    class Meta:
        app_label = "product"
        db_table = "category"
