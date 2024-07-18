from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from enum import Enum
from user.models import ServiceUser


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
    tags = models.CharField(max_length=128, blank=True)
    search_vector = SearchVectorField(null=True)

    class Meta:
        app_label = "product"
        db_table = "product"
        indexes = [
            models.Index(fields=["status", "price"]),
            GinIndex(fields=["search_vector"]),
            GinIndex(
                name="product_name_gin_index",
                fields=["name"],
                opclasses=["gin_bigm_ops"],
            ),
        ]


class Category(models.Model):
    name = models.CharField(max_length=32)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="children"
    )

    class Meta:
        app_label = "product"
        db_table = "category"


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class Order(models.Model):
    user = models.ForeignKey(
        ServiceUser, on_delete=models.CASCADE, related_name="orders"
    )
    total_price = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=8, default=OrderStatus.PENDING
    )  # pending | paid | cancelled
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "product"
        db_table = "order"
        indexes = [
            models.Index(fields=["user", "status"]),
        ]


class OrderLine(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_lines"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    discount_rate = models.FloatField(default=1)

    class Meta:
        app_label = "product"
        db_table = "order_line"
