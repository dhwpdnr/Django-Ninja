import pytest
from product.models import Product
from schema import Schema


@pytest.mark.django_db
def test_product_list(api_client):
    Product.objects.create(name="청바지", price=1, status="active")

    response = api_client.get("/products")

    assert response.status_code == 200
    assert len(response.json()["results"]["products"]) == 1
    assert Schema(
        {
            "results": {
                "products": [
                    {
                        "id": 1,
                        "name": "청바지",
                        "price": 1,
                    }
                ]
            }
        }
    ).validate(response.json())
