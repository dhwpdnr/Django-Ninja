from ninja import Schema
from typing import List


class ProductDetailResponse(Schema):
    id: int
    name: str
    price: int


class ProductListResponse(Schema):
    product: List[ProductDetailResponse]
