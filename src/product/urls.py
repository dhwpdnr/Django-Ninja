from ninja import Router
from django.http import HttpRequest
from .models import Product, ProductStatus
from .response import ProductListResponse
from shared.response import ObjectResponse, response

router = Router(tags=["Products"])


@router.get("", response={200: ObjectResponse[ProductListResponse]})
def product_list_handler(request: HttpRequest):
    return 200, response(
        ProductListResponse(
            products=Product.objects.filter(status=ProductStatus.ACTIVE).values(
                "id", "name", "price"
            )
        )
    )
