import logging
import os

import httpx

from app.core.exceptions import NotFoundException, AppException, ValidationException

logger = logging.getLogger(__name__)

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8000")


class ProductInfo:

    def __init__(self, id: str, name: str, price: float, stock: int, status: str, is_active: bool):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.status = status
        self.is_active = is_active


def fetch_product(product_id: str) -> ProductInfo:
    """Calls Product Service's public GET /{product_id}. Raises
    NotFoundException if the product doesn't exist or isn't visible."""
    url = f"{PRODUCT_SERVICE_URL}/api/v1/products/{product_id}"

    try:
        response = httpx.get(url, timeout=5.0)
    except httpx.RequestError:
        logger.exception("Failed to reach Product Service at %s", url)
        raise AppException("Product service is currently unavailable", status_code=503)

    if response.status_code == 404:
        raise NotFoundException(f"Product {product_id} not found or not available")

    if response.status_code != 200:
        logger.error("Unexpected response from Product Service: %s %s", response.status_code, response.text)
        raise AppException("Failed to verify product", status_code=502)

    data = response.json()

    if data.get("status") != "APPROVED" or not data.get("isActive", False):
        raise ValidationException("Product is not currently available for purchase")

    return ProductInfo(
        id=data["id"],
        name=data["name"],
        price=data["price"],
        stock=data["stock"],
        status=data["status"],
        is_active=data["isActive"],
    )