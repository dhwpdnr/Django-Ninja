from ninja import Schema
from typing import List
from .models import Category


class ProductDetailResponse(Schema):
    id: int
    name: str
    price: int


class ProductListResponse(Schema):
    products: List[ProductDetailResponse]


class CategoryChildResponse(Schema):
    id: int
    name: str


class CategoryParentResponse(Schema):
    id: int
    name: str
    children: List[CategoryChildResponse]

    @staticmethod
    def build(cls, category: Category):
        return cls(
            id=category.id,
            name=category.name,
            children=[
                CategoryChildResponse(id=child.id, name=child.name)
                for child in category.children.all()
            ],
        )


class CategoryListResponse(Schema):
    categories: List[CategoryParentResponse]

    @staticmethod
    def build(cls, categories: List[Category]):
        return cls(
            categories=[
                CategoryParentResponse.build(category) for category in categories
            ]
        )
