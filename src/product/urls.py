from django.db import transaction
from ninja import Router
from django.http import HttpRequest
from django.db.models import F
from django.contrib.postgres.search import SearchQuery

from user.authentication import bearer_auth, AuthRequest
from user.models import ServiceUser, UserPointsHistory, UserPoints

from .models import Product, ProductStatus, Category, Order, OrderLine, OrderStatus
from .request import OrderRequestBody, OrderPaymentConfirmRequestBody
from .response import (
    ProductListResponse,
    CategoryListResponse,
    OrderDetailResponse,
    OkResponse,
)
from .exceptions import (
    OrderInvalidProductException,
    OrderNotFoundException,
    OrderPaymentConfirmFailedException,
    OrderAlreadyPaidException,
    UserPointsNotEnoughException,
)
from user.exceptions import UserVersionConflictException
from .service import payment_service

from shared.response import ObjectResponse, response, ErrorResponse, error_response
from typing import List, Dict

router = Router(tags=["Products"])


@router.get("", response={200: ObjectResponse[ProductListResponse]})
def product_list_handler(
    request: HttpRequest, category_id: int | None = None, query: str | None = None
):
    if query:
        products = Product.objects.filter(
            name__contains=query, status=ProductStatus.ACTIVE
        )

    elif category_id:
        category: Category | None = Category.objects.filter(id=category_id).first()
        if not category:
            products = []
        else:
            category_ids: List[int] = [category.id] + list(
                category.children.values_list("id", flat=True)
            )
            products = Product.objects.filter(
                category_id__in=category_ids, status=ProductStatus.ACTIVE
            ).values("id", "name", "price")
    else:
        products = Product.objects.filter(status=ProductStatus.ACTIVE).values(
            "id", "name", "price"
        )
    return 200, response(ProductListResponse(products=products))


@router.get("/categories", response={200: ObjectResponse[CategoryListResponse]})
def category_list_handler(request: HttpRequest):
    return 200, response(
        CategoryListResponse.build(
            categories=Category.objects.filter(parent=None).prefetch_related("children")
        )
    )


@router.post(
    "/orders",
    response={
        200: ObjectResponse[OrderDetailResponse],
        400: ObjectResponse[ErrorResponse],
    },
    auth=bearer_auth,
)
def order_products_handler(request: AuthRequest, body: OrderRequestBody):
    product_id_to_quantity: Dict[int, int] = body.product_id_to_quantity
    products: List[Product] = list(
        Product.objects.filter(id__in=product_id_to_quantity)
    )

    if len(products) != len(product_id_to_quantity):
        return 400, error_response(msg=OrderInvalidProductException.message)

    with transaction.atomic():
        total_price: int = 0
        order = Order.objects.create(user=request.user)

        order_lines_to_create: List[OrderLine] = []

        for product in products:
            price: int = product.price
            discount_ratio: float = 0.9
            quantity: int = product_id_to_quantity[product.id]

            order_lines_to_create.append(
                OrderLine(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price,
                    discount_rate=discount_ratio,
                )
            )

            total_price += price * quantity * discount_ratio

        order.total_price = total_price
        order.save()
        OrderLine.objects.bulk_create(objs=order_lines_to_create)
    return 201, response({"id": order.id, "total_price": order.total_price})


@router.post(
    "/orders/{order_id}/confirm",
    response={
        200: ObjectResponse[OkResponse],
        400: ObjectResponse[ErrorResponse],
        404: ObjectResponse[ErrorResponse],
    },
    auth=bearer_auth,
)
def confirm_order_payment_handler(
    request: AuthRequest, order_id: int, body: OrderPaymentConfirmRequestBody
):
    if not (order := Order.objects.filter(id=order_id, user=request.user).first()):
        return 404, error_response(msg=OrderNotFoundException.message)

    # if not payment_service.confirm_payment(
    #     payment_key=body.payment_key, amount=order.total_price
    # ):
    #     return 400, error_response(msg=OrderPaymentConfirmFailedException.message)

    with transaction.atomic():
        success: int = Order.objects.filter(
            id=order_id, status=OrderStatus.PENDING
        ).update(status=OrderStatus.PAID)

        if not success:
            return 400, error_response(msg=OrderAlreadyPaidException.message)

        last_points = (
            UserPoints.objects.filter(user=request.user).order_by("-id").first()
        )

        if last_points.points_sum < order.total_price:
            return 400, error_response(msg=UserPointsNotEnoughException.message)

        UserPoints.objects.create(
            user=request.user,
            version=last_points.version + 1,
            points_change=-order.total_price,
            points_sum=last_points.points_sum - order.total_price,
        )

    return 200, response(OkResponse())
